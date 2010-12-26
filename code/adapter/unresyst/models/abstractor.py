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
    
    relationship_type = models.CharField(max_length=MAX_LENGTH_ENTITY_TYPE, \
                    choices=ENTITY_TYPE_CHOICES)
    """A string indicating whether it's a subject, object or both.s/o/so"""

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

    def get_linear_expectancy(self, _redirect_to_leaf=True):
        """Gets the linearly aggregated parameters for instance expectancy.
        In this class returns the weight.
        
        @type redirect_to_leaf: bool
        @param redirect_to_leaf: if True, the call is redirected to the leaf class.
            When called from outside _redirect_to_leaf should always be True, unless
            it's sure it's called on the leaf class instance.
        
        @rtype: float from [0, 1]
        @return: the aggregated expectancy.
        """
        
        # redirect to leaf or not
        if _redirect_to_leaf:
            return self.as_leaf_class().get_linear_expectancy(_redirect_to_leaf=False)
        
        return self.definition.as_leaf_class().weight


class RuleInstance(RelationshipInstance):
    """The rule applied to a pair of subjects/objects.""" 
    
    expectancy = models.FloatField()
    """The probability of the relationship between subject/object.
    A number from [0, 1].
    """
    
    def get_linear_expectancy(self, _redirect_to_leaf=True):
        """Gets the linearly aggregated parameters for instance expectancy.
        Multiplies the base class weight by expectancy.

        @type redirect_to_leaf: bool
        @param redirect_to_leaf: if True, the call is redirected to the leaf class.
            When called from outside _redirect_to_leaf should always be True, unless
            it's sure it's called on the leaf class instance.        
        
        @rtype: float from [0, 1]
        @return: the aggregated expectancy.
        """
        base_expectancy = super(RuleInstance, self).get_linear_expectancy(
                                                    _redirect_to_leaf=False)
        
        return base_expectancy * self.expectancy
        
    class Meta:
        app_label = 'unresyst'
