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

    are_subjects_objects = models.BooleanField()
    """Are subjects == objects for the recommender?"""    
        
    class Meta:
        app_label = 'unresyst'

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name        


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
    

    class Meta:
        app_label = 'unresyst'    
        
        unique_together = ('id_in_specific', 'entity_type', 'recommender')
        """There can be only one subject/object with the given id and 
        recommender.
        """
        
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name        
    
    @classmethod
    def get_domain_neutral_entity(cls, domain_specific_entity, entity_type, recommender):
        """Get domain neutral representation of the given domain specific entity
        (subject/object/subjectobject)
        
        @type domain_specific_entity: django.db.models.Model
        @param domain_specific_entity: the domain specific subject/object/
            subjectobject for which the domain neutral repre should be got
        
        @type entity_type: str
        @param entity_type: 'S'/'O'/'SO' .. see constants, determines whether
            the entity is a subject, object or both
        
        @type recommender: models.Recommender
        @param recommended: the recommender the for which the entity should 
            be got
        
        @rtype: models.SubjectObject
        @returns: the domain neutral representation of the entity        
        
        @raise MultipleObjectsReturned: when there's a broken constraint in 
            the unresyst database (hopefully never)
        @raise DoesNotExist: when the domain neutral representation for 
            the given entity does not exist
        """
        return cls.objects.get(
            id_in_specific=domain_specific_entity.id,
            entity_type=entity_type,
            recommender=recommender)
    
    def get_domain_specific_entity(self, entity_manager):
        """Get domain specific subject/object/both for this universal 
        representation.
        
        @type entity_manager: django.db.models.manager.Manager
        @param entity_manager: the manager over the model containing 
            the domain specific subjects/objects/bot
        
        @rtype: models.Model
        @returns: the domain specific entity for this universal representation
        
        @raise MultipleObjectsReturned: when there's a broken constraint in 
            the client database (hopefully never)
        @raise DoesNotExist: when the domain specific entity for 
            this universal entity does not exist
        """
        return entity_manager.get(id=self.id_in_specific)

    @classmethod
    def unique_pairs(cls, recommender, entity_type):
        """A generator looping through the pairs of subjectobjects so that each two 
        object set is returned only once. 
        
        E.g. after (a, b), the (b, a) pair isn't returned. 
        It doesn't return pairs like (a, a).
        
        Useful for symmetric rule and relationship evaluation.
        
        @type recommender: models.Recommender
        @param recommender: the recommender model for which the pairs should be
            obtained

        @type entity_type: str ('S', 'O' or 'SO') or None
        @param entity_type: the entity type from whic the pair should be taken,
            if None, all entity types are taken
        
        @rtype: generator for two-tuples
        @returns: pairs of subjectobjects entity_type entities belonging to 
            the recommender.
        """
        ent_type_kwargs = {} if entity_type is None \
                            else {'entity_type': entity_type}
        
        # get the subjectobjects to iterate over
        qs_entities = cls.objects.filter(
            recommender=recommender, 
            **ent_type_kwargs).order_by('id')

        # the number of entities
        entity_count = qs_entities.count()             
            
        # get the first argument and the number of entities that 
        # will be taken as the second arg. Starting from 1, 
        # finishing at <count -1>.
        # The first entity will never be used as second argument 
        for arg1, count in zip( \
            qs_entities[1:].iterator(), \
            range(1, entity_count)):

            # obtain only first count entities
            for arg2 in qs_entities[:count].iterator():

                yield (arg1, arg2)
