"""The models that are common to the whole unresyst application."""

from django.db import models

from unresyst.constants import *

class Recommender(models.Model):
    """The representation of a recommender. 
    
    There can be multiple recommenders for one parent system.
    """
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name of the recommender"""
    
    class_name = models.CharField(max_length=MAX_LENGTH_CLASS_NAME, unique=True)
    """The name of the recommender class. Has to be unique."""

    # mozna jeste jestli jsou subjects == objects
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name
        
    class Meta:
        app_label = 'unresyst'
        

class SubjectObject(models.Model):
    """The common representation for a subject and an object."""
    
    id_in_specific = models.IntegerField()
    """The id of the subject/object in the domain-specific system."""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """A textual characterization of the subject/object"""
    
    entity_type = models.CharField(max_length=MAX_LENGTH_ENTITY_TYPE, \
                    choices=ENTITY_TYPE_CHOICES)
    """A string indicating whether it's a subject, object or both.s/o/so"""
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender to which the subject/object belongs."""
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name

    class Meta:
        app_label = 'unresyst'    
        
        unique_together = ('id_in_specific', 'entity_type', 'recommender')
        """There can be only one subject/object with the given id and 
        recommender.
        """
        
        
