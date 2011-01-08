"""The classes for representing business rules and relationships"""

from unresyst.constants import *

from unresyst.models.abstractor import *
from unresyst.models.common import SubjectObject
from unresyst.exceptions import DescriptionKeyError, ConfigurationError

class _Relationship(object):
    """A base class for representing all relationships and rules.
    
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
    
    DefinitionClass = RuleRelationshipDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """
        
    is_symmetric = False
    """Is the rule/relationship between the entities of the same domain?
    True for S-S, O-O, SO-SO
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
        try:
            desc = self.description % format_dict
        except KeyError, e:
            raise DescriptionKeyError(
                message="There's an invalid key in description",
                name=self.name, 
                key=e.__str__(), 
                permitted_keys=format_dict.keys()
            )
        
        return desc
        
    def get_create_definition_kwargs(self):
        """Get dictionary of parameters for the definition model constructor.        
        
        @rtype: dictionary string: object
        @return: the kwargs of the definition model constructor 
        """
        return {
            "name": self.name,
            "recommender": self.recommender.recommender_model,
        }
    
    def get_additional_instance_kwargs(self, ds_arg1, ds_arg2):
        """Get dictionary of additional kwargs for creating the rule/relationship
        instance. 
        
        @type ds_arg1: django.db.models.manager.Manager
        @param ds_arg1: the first argument of the rule instance - domain specific
                
        @type ds_arg2: django.db.models.manager.Manager
        @param ds_arg2: the second argument of the rule instance - domain specific
        
        @rtype: dictionary string: object
        @return: additional keyword args for creating rule/relationship instance 
        """
        return {}
    
    
    def evaluate_on_args(self, arg1, arg2, definition):        
        """Evaluates the rule on the given arguments. If evaluated positively,
        a new rule/relationship instance is saved.
       
        @type arg1: models.SubjectObject
        @param arg1: a domain neutral representation of the first entity.

        @type arg2: models.SubjectObject
        @param arg2: a domain neutral representation of the second entity.
        
        @type definition: models.abstractor.RuleRelationshipDefinition
        @param definition: the model representing the rule/relationship 
            definition
        """
  
        # get the domain specific objects for our universal representations
        #
        arg1_manager = self.recommender._get_entity_manager(arg1.entity_type)
        ds_arg1 = arg1.get_domain_specific_entity(entity_manager=arg1_manager)
        
        arg2_manager = self.recommender._get_entity_manager(arg2.entity_type)
        ds_arg2 = arg2.get_domain_specific_entity(entity_manager=arg2_manager)

        # if the condition is satisfied
        if self.condition(ds_arg1, ds_arg2):
            
            
            add_kwargs = self.get_additional_instance_kwargs(ds_arg1, ds_arg2)
            
            # create a rule/relationship instance
            instance = self.InstanceClass(
                            definition=definition,
                            subject_object1=arg1,
                            subject_object2=arg2,
                            description=self.get_filled_description(arg1, arg2),
                            **add_kwargs)
            
            instance.save()
    
    def evaluate(self):
        """Evaluate the rule on all subjects/objects - pairs.
        
        Creates and saves the rule/relationship definition, creates and saves
        rule instances.        
        """
        
        # obtain the kwargs for creating the definition
        def_kwargs = self.get_create_definition_kwargs()

        # create and save the definition
        definition = self.DefinitionClass(**def_kwargs)
        definition.save()
            
        # parse what should be used as condition args
        arg1_s, arg2_s = self.relationship_type.split(RELATIONSHIP_TYPE_SEPARATOR)        
        
        if arg1_s == arg2_s:
                                                           
            # loop only through the matrix members below the diagonal 
            # 
            for arg1, arg2 in SubjectObject.unique_pairs(
                                recommender=self.recommender.recommender_model,
                                entity_type=arg1_s):                          
                # evaluate it
                self.evaluate_on_args(arg1, arg2, definition)
            
        else:
            # filter subjectobjects for my recommender
            qs_recommender = SubjectObject.objects.filter(
                recommender=self.recommender.recommender_model)
        
            # go through all things that have to be as first and as second param
            for arg1 in qs_recommender.filter(entity_type=arg1_s).iterator():
                for arg2 in qs_recommender.filter(entity_type=arg2_s).iterator():
               
                    # evaluate the rule/relationship on the given args
                    self.evaluate_on_args(arg1, arg2, definition)

  
class PredictedRelationship(_Relationship):
    """A class for representing the predicted relationship."""

    DefinitionClass = PredictedRelationshipDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """    

class _WeightedRelationship(_Relationship):
    """A class representing a relationship with a weight."""

    def __init__(self, name, condition, is_positive, weight, description=None):
        """The constructor."""
        
        super(_WeightedRelationship, self).__init__(name, condition, description)
        
        self.is_positive = is_positive
        """Is the relationship positive to the predicted relationship?"""
        
        self.weight = weight
        """A float number from [0, 1] representing the *static* weight of the rule. 
        It doesn't depend on the entity pair.
        """


    def get_create_definition_kwargs(self):
        """Get dictionary of parameters for the definition model constructor.        
        
        Add the weight to the parameters. 
        
        @rtype: dictionary string: object
        @return: the kwargs of the definition model constructor 
        
        @raise ConfigurationError: if the weight isn't from [0, 1]
        """
        ret_dict = super(_WeightedRelationship, self).get_create_definition_kwargs()
        
        ret_dict['is_positive'] = self.is_positive

        if not (MIN_WEIGHT <= self.weight <= MAX_WEIGHT):
            raise ConfigurationError(
                message=("The rule/relationship '%s' has weight %f," + \
                    " should be between 0 and 1.") % (self.name, self.weight),
                parameter_name="Recommender.rules or Recommender.relationships",
                parameter_value=(self.recommender.rules, self.recommender.relationships)
            )
        
        ret_dict['weight'] = self.weight
        ret_dict["relationship_type"] = self.relationship_type      
        
        return ret_dict
        
    DefinitionClass = RuleRelationshipDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """    
        

class SubjectObjectRelationship(_WeightedRelationship):
    """A class for representing subject-object preference for recommendation"""
    
    relationship_type = RELATIONSHIP_TYPE_SUBJECT_OBJECT
    """The type of the relationship S-O""" 


class _SimilarityRelationship(_WeightedRelationship):
    """A base class (abstract) for all relationships operating between the same type 
    and meaning similarity.
    """
    
    is_symmetric = True
    """For documentation see the base class"""
    

class ObjectSimilarityRelationship(_SimilarityRelationship):
    """A class for representing inter-object similarity."""    

    relationship_type = RELATIONSHIP_TYPE_OBJECT_OBJECT
    """The type of the relationship O-O"""    


class SubjectSimilarityRelationship(_SimilarityRelationship):
    """A class for representing inter-subject similarity."""

    relationship_type = RELATIONSHIP_TYPE_SUBJECT_SUBJECT
    """The type of the relationship S-S"""


class SubjectObjectSimilarityRelationship(_SimilarityRelationship):
    """A class used only when subject domain equals object domain. 
    For representing inter-entity similarity.
    """
    
    relationship_type = RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT
    """The type of the relationship SO-SO"""


# rules:
# 

class _BaseRule(_WeightedRelationship):
    """A base class for all rules (abstract)."""
    
    InstanceClass = RuleInstance
    """The model class used for representing instances of 
    the rule/relationship"""
    
    def __init__(self, name, condition, is_positive, weight, confidence, description=None):
        """The constructor.""" 

        super(_BaseRule, self).__init__(name, condition, is_positive, weight, description)
        
        self.confidence = confidence
        """A float function giving values from [0, 1] representing the 
        the confidence of the rule on the given pair. 
        It's dynamic, depends on the entity pair.
        """                
    
    def get_additional_instance_kwargs(self, ds_arg1, ds_arg2):
        """See the base class for documentation
        
        @raise ConfigurationError: if the confidence function returns a value
            outside [0, 1]
        """
        ret_dict = super(_BaseRule, self).get_additional_instance_kwargs(
                                            ds_arg1, ds_arg2)

        confidence = self.confidence(ds_arg1, ds_arg2)
        
        if not (0.0 <= confidence <= 1.0):
            raise ConfigurationError(
                message=("The rule '%s' has a confidence %f, for the" + \
                    "  pair (%s, %s). Should be between 0 and 1.") % \
                        (self.name, confidence, ds_arg1, ds_arg2),
                parameter_name="Recommender.rules",
                parameter_value=self.recommender.rules
            )
        
        ret_dict['confidence'] = confidence
        return ret_dict
        
        
# confidence by taky mohla vracet string s doplnujicim vysvetlenim,         

class _SimilarityRule(_BaseRule):
    """A base class (abstract) for all rules operating between the same type 
    and meaning similarity."""

    is_symmetric = True
    """For documentation see the base class"""    
    

class ObjectSimilarityRule(_SimilarityRule):
    """A class for representing inter-object similarity."""    

    relationship_type = RELATIONSHIP_TYPE_OBJECT_OBJECT
    """The type of the relationship O-O""" 


class SubjectSimilarityRule(_SimilarityRule):
    """A class for representing inter-subject similarity."""

    relationship_type = RELATIONSHIP_TYPE_SUBJECT_SUBJECT
    """The type of the relationship S-S"""    


class SubjectObjectRule(_BaseRule):
    """A class for representing subject-object preference for recommendation"""

    relationship_type = RELATIONSHIP_TYPE_SUBJECT_OBJECT
    """The type of the relationship S-O"""    

class SubjectObjectSimilarityRule(_SimilarityRelationship):
    """A class used only when subject domain equals object domain. 
    For representing inter-entity rule.
    """
    
    relationship_type = RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT
    """The type of the relationship SO-SO"""

class Bias(object):
    pass    