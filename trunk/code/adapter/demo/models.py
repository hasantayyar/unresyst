"""Demo models for the demo application"""

from django.db import models
from django.contrib.auth.models import User as DjangoUser

class ShoePair(models.Model):
    """A model for a pair of shoes."""
    
    size = models.PositiveSmallIntegerField()
    """The size of the shoe in european shoe size system."""

class User(DjangoUser):
    """A model for the users of the demo system."""
    
    shoe_size = models.PositiveSmallIntegerField(null=True, blank=True)
    """The size of user's shoe in european shoe size system."""
    
    shoes = models.ManyToManyField(ShoePair)
    """User's shoes."""

    
    
    
