"""Base classes for the unresyst application."""

from django.db import models

from symmetric import SymmetricalRelationship
        

class BaseRelationshipInstance(SymmetricalRelationship):
    """An abstract class, the base class of all s-o, s-s, o-o relationships."""

    subject_object1 = models.ForeignKey('unresyst.SubjectObject', \
                        related_name='%(class)s_relationships1')
    """The first subject/object that is in the relationship."""                        
    
    subject_object2 = models.ForeignKey('unresyst.SubjectObject', \
                        related_name='%(class)s_relationships2')
    """The second subject/object that is in the relationship"""              
    
    explanation = models.TextField(default='', blank=True)
    """The explanation of the relationship."""          
        
        
    attr_name1 = 'subject_object1'
    """Overriden attribute name 1"""
    
    attr_name2 = 'subject_object2'
    """Overriden attribute name 2"""

    class Meta:
        abstract = True                
        app_label = 'unresyst'
        
