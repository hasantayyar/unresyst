"""Base classes for the unresyst application."""

from django.db import models
from django.contrib.contenttypes.models import ContentType

from symmetric import SymmetricalRelationship
        

class BaseRelationshipInstance(SymmetricalRelationship):
    """An abstract class, the base class of all s-o, s-s, o-o relationships."""

    subject_object1 = models.ForeignKey('unresyst.SubjectObject', \
                        related_name='%(class)s_relationships1')
    """The first subject/object that is in the relationship."""                        
    
    subject_object2 = models.ForeignKey('unresyst.SubjectObject', \
                        related_name='%(class)s_relationships2')
    """The second subject/object that is in the relationship"""              
    
    description = models.TextField(default='', blank=True)
    """The description of the relationship/rule instance."""          
        
        
    attr_name1 = 'subject_object1'
    """Overriden attribute name 1"""
    
    attr_name2 = 'subject_object2'
    """Overriden attribute name 2"""

    class Meta:
        abstract = True                
        app_label = 'unresyst'        


class ContentTypeModel(models.Model):
    """An abstract base class for all models having some subclasses whose
    instances shouldn't be always returned
    
    Be careful when using multiple inheritance: this class shouldbe used
        as the last and save() shouldn't be overriden in none of the other
        base classes
    """

    content_type = models.ForeignKey(ContentType,editable=False, null=True)
    """The actual type of the object."""
    
    @classmethod
    def remove_subclass_objects(cls):
        """Get instances only of this class"""
        # get the content type
        cont_type = ContentType.objects.get_for_model(cls)
        
        # return only this cont type
        return cls.objects.filter(content_type=cont_type)

    def save(self,*args, **kwargs):
        """Save with the right content type"""
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        
        super(ContentTypeModel, self).save(*args, **kwargs)


    class Meta:
        abstract = True                
        app_label = 'unresyst'
