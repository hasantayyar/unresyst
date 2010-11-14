"""The models that are common to the whole unresyst application."""

from django.db import models

from constants import *

class Recommender(models.Model):
    """The representation of a recommender. 
    
    There can be multiple recommenders for one parent system.
    """
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name of the recommender"""
    
    class_name = models.CharField(max_length=MAX_LENGTH_CLASS_NAME, unique=True)
    """The name of the recommender class. Has to be unique."""



class SubjectObject(models.Model):
    """The common representation for a subjects and objects."""
    
    id_in_specific = models.IntegerField()
    """The id of the subject/object in the domain-specific system."""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """A textual characterization of the subject/object"""
    
    entity_type = 
    """A string indicating whether it's a subject, object or both.s/o/so"""
