"""Models which instances are created by the abstractor package.

A representation of each defined role and relationship.
"""

from django.db import models

from unresyst.constants import *
from base import BaseRelationshipInstance, ContentTypeModel

# Definitions:
#

class PredictedRelationshipDefinition(ContentTypeModel):
    """A definition of the relationship that should be predicted. There's only
    one for a recommender.
    """
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender to which the definition belongs"""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name of the relationship"""        

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name 
    
    class Meta:
        app_label = 'unresyst'
               

class RuleRelationshipDefinition(PredictedRelationshipDefinition):
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
    """
    
    definition = models.ForeignKey(PredictedRelationshipDefinition)
    """The definition of the relationship."""
    
    class Meta:
        app_label = 'unresyst' 
        
        unique_together = ('subject_object1', 'subject_object2', 'definition')
        """For each definition there can be only one subject-object pair."""

    
class RuleInstance(RelationshipInstance):
    """The rule applied to a pair of subjects/objects."""    
    
    expectancy = models.FloatField()
    """The probability of the relationship between subject/object.
    A number from [0, 1].
    """
    
    class Meta:
        app_label = 'unresyst'
