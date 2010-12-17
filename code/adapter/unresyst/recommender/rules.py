"""The classes for representing business rules and relationships"""

from unresyst.constants import *

from unresyst.models.abstractor import *
from unresyst.models.common import SubjectObject

class Relationship(object):
    """A class for representing the predicted relationship.
    
    A subclass for all classes representing a relationship between entities (not necessarily 
    of the same type). Contains the condition that is true between and only 
    between the entities that are in the given relationship.
    """
    
    def __init__(self, name, condition, description=None):
        """The constructor."""
        
        self.name = name
        """The name of the rule/relationship."""
        
        self.condition = condition
        """A boolean function that represents the condition. If True 
        for the given pair of entities, there's the Relationship between the 
        entities. 
        Should be simple.
        """
        
        self.description = description
        """A string describing the rule. It can contain placeholders for entities: 
        
         - %(subject)s, %(object)s for subject-object relationships and rules
         - %(subject1)s, %(subject2)s for subject-subject relationships 
            and rules
         - %(object1)s, %(object2)s for object-object relationships and rules
         - %(subjectobject1)s, %(subjectobject2)s for recommenders where 
            subject domain is the same as object domain        
        """
        
    
    DESCRIPTION_FORMAT_DICT = {
        RELATIONSHIP_TYPE_SUBJECT_OBJECT: 
            (FORMAT_STR_SUBJECT, FORMAT_STR_OBJECT),
        RELATIONSHIP_TYPE_SUBJECT_SUBJECT: 
            (FORMAT_STR_SUBJECT1, FORMAT_STR_SUBJECT2),
        RELATIONSHIP_TYPE_OBJECT_OBJECT: 
            (FORMAT_STR_OBJECT1, FORMAT_STR_OBJECT2),
        RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT: 
            (FORMAT_STR_SUBJECTOBJECT1, FORMAT_STR_SUBJECTOBJECT2)
    }
    """A dictionary relationship type (e.g. 'S-O') a pair of formatting strings 
    for description, e.g. ('subject', 'object').
    """

    relationship_type = RELATIONSHIP_TYPE_SUBJECT_OBJECT
    """The type of the relationship S-O"""
    
    InstanceClass = RelationshipInstance
    """The model class used for representing instances of the rule/relationship"""
    
    DefinitionClass = PredictedRelationshipDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """
    
    def get_filled_description(self, arg1, arg2):
        """Get description for a rule/relationship instance, between 
        arg1 and arg2. 
        
        @type arg1: models.SubjectObject
        @param arg1: the first subjectobject in the relationship/rule

        @type arg2: models.SubjectObject
        @param arg2: the second subjectobject in the relationship/rule
        
        @rtype: str
        @return: a string with filled gaps for entities.
        """
        # get the format strings, e.g. ('subject', 'object')
        format_strings = self.DESCRIPTION_FORMAT_DICT[self.relationship_type]
        
        # create the formating strings to be passed to description
        format_dict = {
            format_strings[0]: arg1,
            format_strings[1]: arg2
        }
        return self.description % format_dict
        
    def get_create_definition_kwargs(self, recommender):
        """Get dictionary of parameters for the definition model constructor.
        
        @type recommender: models.Recommender
        @param recommender: the recommender to which the rule belongs
        
        @rtype: dictionary string: object`
        @return: the kwargs of the definition model constructor 
        """
        return {
            "name": self.name,
            "recommender": recommender
        }
    
    def get_create_instance_kwargs(self, recommender, definition, arg1, arg2):
        """Get dictionary of parameters for the rule instance model
        
        @type recommender: models.Recommender
        @param recommender: the recommender to which the rule belongs
        
        @rtype: dictionary string: object
        @return: the kwargs of the instance model constructor        
        """
        return {
            'definition': definition,
            'subject_object1': arg1,
            'subject_object2': arg2,
            'description': self.get_filled_description(arg1, arg2)
        }
    
    def evaluate(self):
        """Evaluate the rule on all subjects/objects - pairs.
        
        Creates and saves the rule/relationship definition, creates and saves
        rule instances.        
        """
        
        # obtain the kwargs for creating the definition
        def_kwargs = self.get_create_definition_kwargs(self.recommender.recommender_model)

        # create and save the definition
        definition = self.DefinitionClass(**def_kwargs)
        definition.save()
            
        # parse what should be used as condition args
        arg1_s, arg2_s = self.relationship_type.split(RELATIONSHIP_TYPE_SEPARATOR)
        
        if arg1_s == arg2_s:
            #TODO: nejak to vychytat
            pass
        else:
            # go through all things that have to be as first and as second param
            for arg1 in SubjectObject.objects.filter(entity_type=arg1_s).iterator():
                for arg2 in SubjectObject.objects.filter(entity_type=arg2_s).iterator():
                    
                    # get the domain specific objects for our universal representations
                    ds_arg1 = arg1.get_domain_specific_entity(self.recommender.subjects)
                    ds_arg2 = arg2.get_domain_specific_entity(self.recommender.objects)
                    
                    # if the condition is satisfied
                    if self.condition(ds_arg1, ds_arg2):
                        instance_kwargs = self.get_create_instance_kwargs(
                            recommender=self.recommender.recommender_model,
                            definition=definition,
                            arg1=arg1,
                            arg2=arg2
                        )
                        
                        instance = self.InstanceClass(**instance_kwargs)
                        instance.save()
                        
        """
        r (relationship/rule)                
        
        if <to co ma byt vpravo> == <to co ma byt vlevo>:
            nejak vychytat, aby se to pro kazdy par delalo jen jednou
        else    
        for so1 in <to co ma byt vlevo>:
            for so2 in <to co ma byt vpravo>:
                if r.condition(so1, so2):
                    create instance including expectancy
                    save
        """        

        


class _WeightedRelationship(Relationship):
    """A class representing a relationship with a weight."""

    def __init__(self, name, condition, weight, description=None):
        """The constructor."""
        
        super(_WeightedRelationship, self).__init__(name, condition, description)
        
        self.weight = weight
        """A float number from [0, 1] representing the *static* weight of the rule. 
        It doesn't depend on the entity pair.
        """        
        
        

class SubjectObjectRelationship(_WeightedRelationship):
    """A class for representing subject-object preference for recommendation"""
    pass 

class _SimilarityRelationship(_WeightedRelationship):
    """A base class (abstract) for all relationships operating between the same type 
    and meaning similarity.
    """
    pass
    

class ObjectSimilarityRelationship(_SimilarityRelationship):
    """A class for representing inter-object similarity."""    
    pass


class SubjectSimilarityRelationship(_SimilarityRelationship):
    """A class for representing inter-subject similarity."""
    pass

# rules:
# 

class _BaseRule(_WeightedRelationship):
    """A base class for all rules (abstract)."""
    
    def __init__(self, name, condition, weight, expectancy, description=None):
        """The constructor."""
        
        super(_BaseRule, self).__init__(name, condition, weight, description)
        
        self.expectancy = expectancy
        """A float function giving values from [0, 1] representing the confidence
        of the rule for the given pair. It's dynamic, depends on the entity pair.
        """
        
        
# confidence by taky mohla vracet string s doplnujicim vysvetlenim,         

class _SimilarityRule(_BaseRule):
    """A base class (abstract) for all rules operating between the same type 
    and meaning similarity."""
    pass
    

class ObjectSimilarityRule(_SimilarityRule):
    """A class for representing inter-object similarity."""    
    pass


class SubjectSimilarityRule(_SimilarityRule):
    """A class for representing inter-subject similarity."""
    pass


class SubjectObjectRule(_BaseRule):
    """A class for representing subject-object preference for recommendation"""
    pass    

class Bias(object):
    pass    
