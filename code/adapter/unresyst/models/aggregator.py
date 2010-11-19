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

