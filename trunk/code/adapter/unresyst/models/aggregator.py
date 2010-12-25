"""Models which instances are created by the aggregator package.

The aggregated relationship.
"""

from django.db import models
from base import BaseRelationshipInstance

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
    
    additional_unique = ('recommender', )
    """There can be multiple pairs for one recommender"""
    
    class Meta:
        app_label = 'unresyst' 
        
        unique_together = ('subject_object1', 'subject_object2', 'recommender')
        """For each recommender there can be only one subject-object pair."""
