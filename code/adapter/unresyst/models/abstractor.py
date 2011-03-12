"""Models which instances are created by the abstractor package.

A representation of each defined role and relationship.
"""

from django.db import models

from unresyst.constants import *
from base import BaseRelationshipInstance, ContentTypeModel, \
    BaseRelationshipDefinition


def _count_expectancy(is_positive, weight, confidence=1):
    """Count the expectancy for the instance as 1/2 +- weighted_confidence/2 
    .. depending on is_positive.
    
    @type is_positive: bool
    @param is_positive: is the rule/relationship/bias positive for the 
        predicted_relationship?
    
    @type weight: float
    @param weight: the static weight of the rule/relationship/bias

    @type confidence: float
    @param confidence: the confidence of the rule/relationship/bias depending
        on the entity
    
    @rtype: float
    @return: the probability of the predicted_relationship appearing between
        the entities in the pair.
    """
    
    # get factor 
    factor = 1 if is_positive else -1        
    
    return 0.5 + factor * ((weight * confidence) / 2)


# Definitions:
#      

class PredictedRelationshipDefinition(BaseRelationshipDefinition):
    """A definition of a the predicted relationship"""

    class Meta:
        app_label = 'unresyst'    
        
class ExplicitRuleDefinition(BaseRelationshipDefinition):
    """A definition of an explicit feedback rule"""
    
    class Meta:
        app_label = 'unresyst'              


class RuleRelationshipDefinition(BaseRelationshipDefinition):
    """A definition of a rule/relationship. Represents the rule/relationship
    given by the domain expert in the database."""    
    
    weight = models.FloatField()
    """The weight of the rule/relationship. A number from [0, 1]."""
    
    relationship_type = models.CharField(max_length=MAX_LENGTH_RELATIONSHIP_TYPE, 
                    choices=RELATIONSHIP_TYPE_CHOICES)
    """A string indicating whether it's a subject, object or both.s/o/so"""
    
    is_positive = models.BooleanField()
    """Is the rule/relationship positive for the predicted_relationship?"""

    class Meta:
        app_label = 'unresyst' 

    def __unicode__(self):
        """Return a printable representation of the instance"""        
        ret = super(RuleRelationshipDefinition, self).__unicode__()

        return ret + "%f, positive: %s" % (self.weight, self.is_positive)
        
# instances:
#

class RelationshipInstance(BaseRelationshipInstance, ContentTypeModel):
    """The relationship between two subject/objects.
    
    All relationships are "symetrical" in sense that if there is 
    a relationship in the given direction there can't be one in the opposite.
    
    Weight of the relationship is in the definition.
    
    The model also contains the predicted relationship instances.
    """
    
    definition = models.ForeignKey('unresyst.BaseRelationshipDefinition')
    """The definition of the relationship. Pointing to the base, because
    it has to be also for the predicted relationship instances.
    """
    
    additional_unique = ('definition', )
    """There can be multiple pairs for one recommender"""
    
    class Meta:
        app_label = 'unresyst' 
        
        unique_together = ('subject_object1', 'subject_object2', 'definition')
        """For each definition there can be only one subject-object pair."""

    def get_expectancy(self, _redirect_to_leaf=True):
        """Get the instance expectancy counted 
        
        @type redirect_to_leaf: bool
        @param redirect_to_leaf: if True, the call is redirected to the leaf class.
            When called from outside _redirect_to_leaf should always be True, unless
            it's sure it's called on the leaf class instance.
        
        @rtype: float from [0, 1]
        @return: the aggregated expectancy.
        """
        
        # redirect to leaf or not
        if _redirect_to_leaf:
            return self.as_leaf_class().get_expectancy(_redirect_to_leaf=False)
        
        # get the whole object for definition
        leaf_definition = self.definition.as_leaf_class()        
        
        return _count_expectancy(
            is_positive=leaf_definition.is_positive,
            weight=leaf_definition.weight)

    @classmethod
    def filter_predicted(cls, recommender_model):
        """Get queryset of the instances of the predicted relationship.
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender whose instances should
            be aggregated. 

        @rtype: QuerySet
        @returns: instances of the predicted relationship for the given
            recommender
        """
        # get the predicted relationship definition
        pred_rel_def = PredictedRelationshipDefinition.objects.get(
                        recommender=recommender_model)
        
        return cls.objects.filter(definition=pred_rel_def)                        


class ExplicitRuleInstance(BaseRelationshipInstance):
    """The explicit preference of a subject to an object.
    
    The relationship isn't weighted.        
    """
    
    definition = models.ForeignKey('unresyst.ExplicitRuleDefinition')
    """The definition of the relationship.         
    """

    expectancy = models.FloatField()
    """The normalized explicit preference of the given subject to the given 
    object.
    A number from [0, 1].
    """
    
    additional_unique = ('definition', )
    """There can be multiple pairs for one recommender"""
    
    class Meta:
        app_label = 'unresyst' 
        
        unique_together = ('subject_object1', 'subject_object2', 'definition')
        """For each definition there can be only one subject-object pair."""

    def get_expectancy(self, _redirect_to_leaf=True):
        """Get the instance expectancy counted 
        
        @type redirect_to_leaf: bool
        @param redirect_to_leaf: to stay compatible with other classes
        
        @rtype: float from [0, 1]
        @return: the expectancy.
        """        
        return self.expectancy    


class RuleInstance(RelationshipInstance):
    """The rule applied to a pair of subjects/objects.""" 
    
    confidence = models.FloatField()
    """The confidence of the given rule being positive/negative (depending on
    definition.is_positive) in means of the predicted_relationship
    A number from [0, 1].
    """
    
    def get_expectancy(self, _redirect_to_leaf=True):
        """Get the instance expectancy counted as 1/2 +- weight*confidence/2 .. depending on whether
        the relationship is positive.

        @type redirect_to_leaf: bool
        @param redirect_to_leaf: if True, the call is redirected to the leaf class.
            When called from outside _redirect_to_leaf should always be True, unless
            it's sure it's called on the leaf class instance.        
        
        @rtype: float from [0, 1]
        @return: the aggregated expectancy.
        """
        # get the whole object for definition
        leaf_definition = self.definition.as_leaf_class()
        
        return _count_expectancy(
            is_positive=leaf_definition.is_positive,            
            weight=leaf_definition.weight,
            confidence=self.confidence)        
        
    class Meta:
        app_label = 'unresyst'
        
# clusters:
# 

class ClusterSet(models.Model):
    """A set of clusters defined by the user. E.g. 'Gender'."""

    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """A textual characterization of the cluster set."""    
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender to which the cluster set belongs."""    

    entity_type = models.CharField(max_length=MAX_LENGTH_ENTITY_TYPE, \
                    choices=ENTITY_TYPE_CHOICES)
    """A string indicating whether the contained clusters are for subjects,
    objects or both.s/o/so"""

    weight = models.FloatField()
    """The weight of the similarity inferred from two subject/objects 
    belonging to one cluster. A number from [0, 1].
    """

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name  
        
    class Meta:
        app_label = 'unresyst'    
        
        unique_together = ('name', 'recommender')
        """There can be only one cluster set with the given name for 
        a recommender.
        """


class Cluster(models.Model):
    """A cluster (class of subjects/objects) defined by the user.
    E.g. 'Female'"""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """A textual characterization of the cluster"""
    
    cluster_set = models.ForeignKey('unresyst.ClusterSet')
    """The set the cluster belongs to"""
        
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"%s - %s" % (self.cluster_set, self.name)
        
    class Meta:
        app_label = 'unresyst'    
        
        unique_together = ('name', 'cluster_set')
        """There can be only one cluster cluster set of the given name in the 
        cluster set.
        """

class ClusterMember(models.Model):
    """A membership of a subject/object in the cluster."""
    
    cluster = models.ForeignKey('unresyst.Cluster')
    """The cluster"""
    
    member = models.ForeignKey('unresyst.SubjectObject')
    """The cluster member"""
    
    description = models.TextField(default='', blank=True)
    """The description of the membership."""  
    
    confidence = models.FloatField()
    """The confidence of the member belonging to the cluster.
    A number from [0, 1].
    """
    
    def get_expectancy(self):
        """Return the expectancy that will be used for similarity counting 
        for cluster members"""
        
        return _count_expectancy(
            is_positive=True,
            weight=self.cluster.cluster_set.weight,
            confidence=self.confidence)
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"(%s, %s): %f" % (self.cluster, self.member, self.confidence)
        
        
    class Meta:
        app_label = 'unresyst'    
        
        unique_together = ('cluster', 'member')
        """There can be only one membership for a subjectobject in the given 
        cluster.
        """    

# Bias:
#
        
class BiasDefinition(models.Model):
    """The definition of a bias"""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name of the bias"""  
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender to which the definition belongs. 
    """
    
    weight = models.FloatField()
    """The weight of the bias
    belonging to one cluster. A number from [0, 1].
    """
    
    entity_type = models.CharField(max_length=MAX_LENGTH_ENTITY_TYPE, \
                    choices=ENTITY_TYPE_CHOICES)
    """A string indicating whether the contained bias is for subjects,
    objects or both.s/o/so"""
    
    is_positive = models.BooleanField()
    """Is the bias positive (adding a probability) for the predicted_relationship?"""
    
    def __unicode__(self):
        """Return a printable representation of the instance."""
        return self.name
                
    class Meta:
        app_label = 'unresyst'   
        unique_together = ('name', 'recommender')
        """There can be only one bias definition with the given name for 
        a recommender.
        """
 
        
class BiasInstance(models.Model):
    """A bias for a particular subject/object.""" 
    
    confidence = models.FloatField()
    """The confidence of the given bias being positive/negative (depending on
    definition.is_positive) in means of the predicted_relationship
    A number from [0, 1].
    """          
            
    subject_object = models.ForeignKey('unresyst.SubjectObject')
    """The biased subject/object."""
    
    definition = models.ForeignKey('unresyst.BiasDefinition')
    """The definition of the bias.
    """
    
    description = models.TextField(default='', blank=True)
    """The filled description of the bias."""           

                
    class Meta:
        app_label = 'unresyst'        
        unique_together = ('definition', 'subject_object')
        """There can be only one bias for each definition on one subjectobject
        a recommender.
        """        
        
    def __unicode__(self):
        """Return a printable representation of the instance."""
        return u"%s: %s" % (self.definition, self.subject_object)

    def get_expectancy(self):
        """Get the expectancy (probability that the subjectobject will be 
        in the predicted_relationship, according to the bias).
        
        @rtype: float
        @return: expectancy
        """
        return _count_expectancy(
            is_positive=self.definition.is_positive,
            weight=self.definition.weight,
            confidence=self.confidence)
