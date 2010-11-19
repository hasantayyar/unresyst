"""Base classes for the unresyst application."""

from django.db import models

from unresyst.exceptions import SymmetryError, UnresystError as BaseError
        
class SymmetricalRelationship(models.Model):
    """A base class for all symmetrical relationship models. The relationship can't be 
    between the same object."""
    
    attr_name1 = ''
    """The name of the first attribute pointing on some model. Should be overriden"""
    
    attr_name2 = ''
    """The name of the second attribute pointing on some model. Should be overriden"""

    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        """Overrides the save method in order to control the symmetricity.

        @raise SymmetryError: if there's something wrong with the saved entities in the
            means of symmetry                
        """
        
        # get the objects that should be saved as related
        object1 = getattr(self, self.attr_name1)
        object2 = getattr(self, self.attr_name2)
        
        # if they're identical, raise an error
        # the equality of entity models is already solved by overriding the __eq__ method
        if object1 == object2:                        
            raise SymmetryError(
                message="The related objects can't be identical",
                object1=object1, 
                object2=object2)
        
        # if the relationship exists in some direction
        # raise another error.
        #         
        # try the saving direction
        self.__check_save(object1, object2)
                
        # try the other direction
        self.__check_save(object2, object1)
         
        # save the relationship                             
        return super(SymmetricalRelationship, self).save(*args, **kwargs) 
    
    
    def __check_save(self, object1, object2):
        """Check whether the the relationship between the objects in the given direction
        can be saved. If not, throw an exception. Includes checks for update."""
        
        # try finding the relation in the database
        rel = self.__class__.__get_relation(object1, object2)

        # if we have found a relation between object1 and object2
        if rel:
        
            # if it's new value to insert (no id set)
                # or it's a value to update, and the found relationship isn't the same 
                # as the one we're saving
            if not self.id or  \
                (self.id and self.id != rel.id):
                
                # than it's an error.            
                raise SymmetryError(
                    message="The relationship is already in the database.",
                    object1=object1, 
                    object2=object2)    

    @classmethod
    def __get_related_objects_in_attribute(cls, obj, attr_name1, attr_name2):
        """Get objects related to obj that are in the attr_name2 attribute...
        obj is in the attr_name1 attribute."""
        
        # construct the kwargs
        kwargs = {attr_name1: obj}
        
        # get the relationships where obj is in the first attribute
        relationships = cls.objects.filter(**kwargs)
        
        # get the objects that are in the second attribute
        related_objects = [getattr(relationship, attr_name2) for relationship in relationships]
        
        return related_objects
        

    @classmethod    
    def get_related_objects(cls, obj):
        """Get objects that are in relationship with obj.
        
        Returns just objects (not the whole binding items).
        
        @type obj: core.models.BaseEntity
        @param obj: the object whose related objects should be got
        
        @rtype: list of core.models.BaseEntity
        @return: the list of objects related to obj
        """
        # relationships where obj is as the first
        related_objects1 = cls.__get_related_objects_in_attribute(obj, cls.attr_name1, cls.attr_name2)

        # relationships where obj is as the second        
        related_objects2 = cls.__get_related_objects_in_attribute(obj, cls.attr_name2, cls.attr_name1)
                
        return related_objects1 + related_objects2
        
    @classmethod        
    def get_relationships(cls, obj):
        """Get bindings for objects that are in relationship with the object obj.
        
        Returns whole binding items (not just objects).
        
        The related objects can be got using get_related. Example:

        connections = get_relationships(pepa)
        
        for connection in connections:
            print connection.connection_comment
            
            object_connected_to_pepa = connection.get_related(pepa)
            # ...
        
        @type obj: core.models.BaseEntity
        @param obj: the object whose relationships should be got
        
        @rtype: list of relationship class
        @return: the list of relationships related to obj                
        """
        # get relationships where there is cls at first or second place
        # 
        kwargs1 = {cls.attr_name1: obj}
        kwargs2 = {cls.attr_name2: obj}

        from django.db.models import Q
        q = cls.objects.filter(
            Q(**kwargs1) | Q(**kwargs2)
        )

        return list(q)
        
        
    def get_related(self,obj):
        """On a relationship, get the object that is related to obj, no matter in which
        attribute it is.
                
        To be used in the combination with the get_relationships method.

        @type obj: core.models.BaseEntity
        @param obj: the object whose related object should be got
        
        @rtype: core.models.BaseEntity
        @return: the object in the relationship no matter in which attribute it is.
        
        @raise SymmetryError: if the obj isn't a part of the relationship on which 
            the method is called
        """
        # get the objects in the relationship
        object1 = getattr(self, self.attr_name1)
        object2 = getattr(self, self.attr_name2)
        
        # if obj ist the first one, return the second
        # the equality of entity models is already solved by overriding the __eq__ method
        if obj == object1: 
            return object2
            
        # if it's the second, return the first
        if obj == object2:
            return object1
        
        # otherwise return an error
        raise SymmetryError(
            message="The relationship object doesn't contain the '%s' object" % obj,
            object1=object1, 
            object2=object2) 
                
    def contains_object(self, obj):
        """Does the relationship contain the obj object? On one of the sides.
        
        @type obj: object
        @param obj: the object to check whether it's in the relationship
        
        @rtype: bool
        @return: Whether the object is contained on one side of the relationship
        """

        # get the objects in the relationship
        object1 = getattr(self, self.attr_name1)
        object2 = getattr(self, self.attr_name2)                
        
        return obj==object1 or obj==object2

    @classmethod
    def __contains_relation(cls, object1, object2):
        """Does model in database contain the relationship of object1 and object2?"""
        
        return bool(cls.__get_relation(object1, object2))
    
    @classmethod
    def __get_relation(cls, object1, object2): 
        """Get the relation of the two objects in the given direction. If it doesn't exist
        return None"""
        
        # try to get the relationship
        query = cls.objects.filter(
            **{cls.attr_name1: object1,
               cls.attr_name2: object2})

        # if some exists
        if query:
            if query.count() > 1:
                raise BaseError('Database Error - too many obtained relationships')
            
            # return it    
            return query[0]
        
        # otherwise there's nothing
        return None            
        
        
    @classmethod
    def get_relationship(cls, object1, object2):
        """Get the relationship between the two objects if they're related.
        If not return None.
        
        Takes into account both directions of the symmetry.
        
        @type object1: Model
        @param object1: the first object 
        
        @type object2: Model
        @param object2: the second object 
        
        @rtype: relationship object
        @return: the relationship between the two objects or None if they aren't related
        """    
        # try the first direction
        relationship = cls.__get_relation(object1, object2)
        if relationship:
            return relationship  
            
        # try the second
        return cls.__get_relation(object2, object1)              


    @classmethod
    def are_related(cls, object1, object2):
        """Is the object related to other object?
        
        Takes into account both directions of the symmetry.
        
        @type object1: Model
        @param object1: the first object 
        
        @type object2: Model
        @param object2: the second object 
        
        @rtype: bool
        @return: True if they're in relationship, False otherwise. 
        """        
        
        return cls.__contains_relation(object1, object2) \
                or cls.__contains_relation(object2, object1)
                
                

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
        
