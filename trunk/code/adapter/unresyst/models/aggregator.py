"""Models which instances are created by the aggregator package.

The aggregated relationship.
"""

from django.db import models

from base import BaseRelationshipInstance
from unresyst.constants import *

class AggregatedRelationshipInstance(BaseRelationshipInstance):
    """A representation of an aggregated relationship between two subject/objects
    
    There can be only one aggregated relationship for each subject/object pair
    for a recommender.
    """

    expectancy = models.FloatField()
    """The probability of the relationship between subject/object.
    A number from [0, 1].
    """
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender it belongs to"""
    
    relationship_type = models.CharField(max_length=MAX_LENGTH_RELATIONSHIP_TYPE, 
                    choices=RELATIONSHIP_TYPE_CHOICES)
    """A string indicating whether it's a S-O, O-O, S-S, or SO-SO relationship."""
    
    additional_unique = ('recommender', )
    """There can be multiple pairs for one recommender"""

    def __unicode__(self):
        """Return a printable representation of the instance"""        
        ret = super(RuleRelationshipDefinition, self).__unicode__()

        return ret + ", %f" % (self.expectancy)    
 
    class Meta:
        app_label = 'unresyst' 
        
        unique_together = ('subject_object1', 'subject_object2', 'recommender')
        """For each recommender there can be only one subject-object pair."""
        
class AggregatedBiasInstance(models.Model):
    """An aggregated bias of a subjectobject"""        
    
    expectancy = models.FloatField()
    """The probability of the subject/object being in the predicted_relationship
    A number from [0, 1].
    """
    
    subject_object = models.ForeignKey('unresyst.SubjectObject')
    """The biased subject/object."""    
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender it belongs to"""
    
    description = models.TextField(default='', blank=True)
    """The filled description of the aggregated bias."""       
    
    class Meta:
        app_label = 'unresyst' 
        
        unique_together = ('subject_object', 'recommender')
        """For each recommender there can be only one subject-object pair."""    
