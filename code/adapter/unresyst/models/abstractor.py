"""Models which instances are created by the abstractor package.

A representation of each defined role and relationship.
"""

from django.db import models

from unresyst.constants import *
from base import BaseRelationshipInstance, ContentTypeModel, \
    BaseRelationshipDefinition

# Definitions:
#      

class PredictedRelationshipDefinition(BaseRelationshipDefinition):
    """A definition of a the predicted relationship"""

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

    def _count_expectancy(self, weighted_confidence):
        """Count the expectancy for the instance as 1/2 +- weighted_confidence/2 
        .. depending on whether the rule/relationship is positive.
        
        @type weighted_confidence: float
        @param weighted_confidence: the confidence of the rule/relationship 
            including the effect of weight.
        
        @rtype: float
        @return: the probability of the predicted_relationship appearing between
            the entities in the pair.
        """

        # get the whole object for definition
        leaf_definition = self.definition.as_leaf_class()
        
        # get factor 
        factor = 1 if leaf_definition.is_positive else -1        
        
        return 0.5 + factor * (weighted_confidence / 2)


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
        
        # get factor and weight
        weight = leaf_definition.weight        
        
        return self._count_expectancy(weighted_confidence=weight)

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
        
        # get factor and weight
        weight = leaf_definition.weight        
        
        return self._count_expectancy(weight * self.confidence)
        

        
    class Meta:
        app_label = 'unresyst'
