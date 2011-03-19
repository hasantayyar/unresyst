"""The classes for representing business rules and relationships"""

from unresyst.constants import *

from unresyst.models.abstractor import *
from unresyst.models.common import SubjectObject
from unresyst.exceptions import DescriptionKeyError, ConfigurationError

class BaseRelationship(object):
    """A base class for representing all relationships and rules.
    
    A subclass for all classes representing a relationship between entities (not necessarily 
    of the same type). Contains the condition that is true between and only 
    between the entities that are in the given relationship.
    """
    
    def __init__(self, name, condition=None, description=None, generator=None):
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
        
        self.generator = generator
        """A generator returning pairs of objects that are in the relationship/
        the rule applies to them.
        For performance reasons - if given, the pairs will be taken from it 
        without the need for evaluating the condition for each possible pair.
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
        if self.description is None:
            desc = ''
        else:
            try:        
                desc = self.description % format_dict
            except KeyError, e:
                raise DescriptionKeyError(
                    message="There's an invalid key in description",
                    recommender=self.recommender,
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
            "recommender": self.recommender._get_recommender_model(),
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
    
    
    def evaluate_on_dn_args(self, dn_arg1, dn_arg2, definition):        
        """Evaluates the rule on the given arguments. If evaluated positively,
        a new rule/relationship instance is saved.
       
        @type dn_arg1: models.SubjectObject
        @param dn_arg1: a domain neutral representation of the first entity.

        @type dn_arg2: models.SubjectObject
        @param dn_arg2: a domain neutral representation of the second entity.
        
        @type definition: models.abstractor.RuleRelationshipDefinition
        @param definition: the model representing the rule/relationship 
            definition
            
        @rtype: int
        @return: 1 if something has benn created, 0 if not
        """
  
        # get the domain specific objects for our universal representations
        #
        arg1_manager = self.recommender._get_entity_manager(dn_arg1.entity_type)
        ds_arg1 = dn_arg1.get_domain_specific_entity(entity_manager=arg1_manager)
        
        arg2_manager = self.recommender._get_entity_manager(dn_arg2.entity_type)
        ds_arg2 = dn_arg2.get_domain_specific_entity(entity_manager=arg2_manager)

        # if the condition is satisfied
        if self.condition(ds_arg1, ds_arg2):
            
            self._perform_save_instance(definition, ds_arg1, ds_arg2, dn_arg1, dn_arg2)
            return 1
        
        return 0

    @classmethod
    def order_arguments(cls, dn_arg1, dn_arg2):
        """Order the arguments as they appear in the relationship."""
        a1, a2, x, x = cls._order_in_pair(dn_arg1, dn_arg2, None, None)
        
        return (a1, a2)

    @classmethod
    def _order_in_pair(cls, dn_arg1, dn_arg2, ds_arg1, ds_arg2):
        """Swap the arguments in the rule/relationships so that the first
        has a lower id than the second
        """

        # if the second argument has lower id than the first, swap them
        if dn_arg2.pk < dn_arg1.pk: 
            return (dn_arg2, dn_arg1, ds_arg2, ds_arg1)

        # otherwise not
        return (dn_arg1, dn_arg2, ds_arg1, ds_arg2)
        

    def _perform_save_instance(self, definition, ds_arg1, ds_arg2, dn_arg1, dn_arg2):
        """Perform the action of creating and saving the instance"""
        
        # order the instances in pairs as the class requires
        dn_arg1, dn_arg2, ds_arg1, ds_arg2 = self._order_in_pair(dn_arg1, dn_arg2, ds_arg1, ds_arg2)
                       
        add_kwargs = self.get_additional_instance_kwargs(ds_arg1, ds_arg2)
        
        # create a rule/relationship instance
        instance = self.InstanceClass(
                        definition=definition,
                        subject_object1=dn_arg1,
                        subject_object2=dn_arg2,
                        description=self.get_filled_description(dn_arg1, dn_arg2),
                        **add_kwargs)
        
        instance.save()


    def save_instance(self, ds_arg1, ds_arg2, definition):        
        """Save an instance of the rule/relationship for the given args.
       
        @type ds_arg1: domain specific subject/object
        @param ds_arg1: a domain specific representation of the first entity.

        @type ds_arg2: domain specific subject/object
        @param ds_arg2: a domain specific representation of the second entity.
        
        @type definition: models.abstractor.RuleRelationshipDefinition
        @param definition: the model representing the rule/relationship 
            definition
            
        @raise ConfigurationError: thrown if the condition doesn't evaluate 
            to true on the given pair
        """
        if not (self.condition is None) and not self.condition(ds_arg1, ds_arg2):
            raise ConfigurationError(
                message=("The condition wasn't evaluated as true for the pair " + 
                    "%s, %s, even though it was returned by the generator.") % (ds_arg1, ds_arg2), 
                recommender=self.recommender, 
                parameter_name='rules/relationships', 
                parameter_value=self.name)
        
        # convert the domain specific to domain neutral        
        #
        arg1_ent_type, arg2_ent_type = self.relationship_type.split(RELATIONSHIP_TYPE_SEPARATOR) 

        dn_arg1 = SubjectObject.get_domain_neutral_entity(
                    domain_specific_entity=ds_arg1, 
                    entity_type=arg1_ent_type, 
                    recommender=definition.recommender)

        dn_arg2 = SubjectObject.get_domain_neutral_entity(
                    domain_specific_entity=ds_arg2, 
                    entity_type=arg2_ent_type, 
                    recommender=definition.recommender)
        
        # create and save the instance
        self._perform_save_instance(definition, ds_arg1, ds_arg2, dn_arg1, dn_arg2)                  
                    
                            
    
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

        i = 0        
        # if we have a generator, use it for looping through pairs
        if not (self.generator is None):
            

            # loop through pairs, save the rule/relationship instances
            for ds_arg1, ds_arg2 in self.generator():
                self.save_instance(ds_arg1, ds_arg2, definition)
                i += 1
            
            print "    %d instances of rule/rel %s created" % (i, self.name)
            
            # that's it
            return
            
        
        # otherwise take the entities one by one
            
        # parse what should be used as condition args
        arg1_s, arg2_s = self.relationship_type.split(RELATIONSHIP_TYPE_SEPARATOR)        
        
        if arg1_s == arg2_s:
                                                           
            # loop only through the matrix members below the diagonal 
            # 
            i = 0
            for arg1, arg2 in SubjectObject.unique_pairs(
                                recommender=self.recommender._get_recommender_model(),
                                entity_type=arg1_s):                          
                # evaluate it
                i += self.evaluate_on_dn_args(arg1, arg2, definition)
            

            
        else:
            # filter subjectobjects for my recommender
            qs_recommender = SubjectObject.objects.filter(
                recommender=self.recommender._get_recommender_model())
        
            # go through all things that have to be as first and as second param
            for arg1 in qs_recommender.filter(entity_type=arg1_s).iterator():
                for arg2 in qs_recommender.filter(entity_type=arg2_s).iterator():
               
                    # evaluate the rule/relationship on the given args
                    i += self.evaluate_on_dn_args(arg1, arg2, definition)

        print "    %d instances of rule/rel %s created" % (i, self.name)

    
    def export(self, f):
        """Export the relationship as lines to the given file object.
        
        Exports the relationship in form:
        subject_id, object_id[,confidence]\n
        
        confidence is exported only if it's relevant,
        no matter if it's positive or not
        
        @type f: file
        @param f: the file to write to
        
        @raise: ConfigurationError: if the rule/relationship doesn't have
            a generator.
        """
        
        # if we don't have a generator raise an error
        if self.generator is None:
            raise ConfigurationError(
                message="The relationship to export is missing a generator.", 
                recommender=cls, 
                parameter_name='?', 
                parameter_value=cls.name)
            
        i = 0
        
        # loop through pairs, export the rule/relationship instances
        for ds_arg1, ds_arg2 in self.generator():
                        
            # create the common part
            linestr = "%s,%s" % (ds_arg1.pk, ds_arg2.pk)
            
            # get the confidence if provided
            adkwargs = self.get_additional_instance_kwargs(ds_arg1, ds_arg2)
            
            # if confidence provided, append it
            if adkwargs.has_key(EXPECTANCY_KWARG_NAME):
                linestr += ",%f" % adkwargs[EXPECTANCY_KWARG_NAME]
            
            linestr += '\n'
            
            # write it to the file
            f.write(linestr)
            
            i += 1
        
        print "    %d instances of rule/rel %s exported" % (i, self.name)

        
class PredictedRelationship(BaseRelationship):
    """A class for representing the predicted relationship."""

    DefinitionClass = PredictedRelationshipDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """    
    
    @classmethod
    def _order_in_pair(cls, dn_arg1, dn_arg2, ds_arg1, ds_arg2):
        """Swap the arguments in the relationship so that the first
        is always a subject and second the object.
        """    
        
        # for the SO entities we apply the normal policy
        if dn_arg1.entity_type == ENTITY_TYPE_SUBJECTOBJECT:
            return super(PredictedRelationship, cls)._order_in_pair(dn_arg1, dn_arg2, ds_arg1, ds_arg2)

        # otherwise we put subjects as first
        
        # if the first is object, swap
        if dn_arg1.entity_type == ENTITY_TYPE_OBJECT:
            return (dn_arg2, dn_arg1, ds_arg2, ds_arg1)
        
        # if not, keep
        return (dn_arg1, dn_arg2, ds_arg1, ds_arg2)

class ExplicitSubjectObjectRule(BaseRelationship):
    """A class for representing explicit preference like rating, for attributes where
    the user can express both positive and negative preference."""

    relationship_type = RELATIONSHIP_TYPE_SUBJECT_OBJECT
    """The type of the relationship S-O""" 

    DefinitionClass = ExplicitRuleDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """  
    
    InstanceClass = ExplicitRuleInstance
    """The model class used for representing instances of 
    the rule/relationship"""
    
            
    def __init__(self, name, expectancy, condition=None, description=None, generator=None):
        """The constructor."""
        
        super(ExplicitSubjectObjectRule, self).__init__(name, condition, description, generator)
        
        self.expectancy = expectancy
        """A function taking a subject and an object, giving the explicit preference
        normalized to [0, 1].
        """
        
    def get_additional_instance_kwargs(self, ds_arg1, ds_arg2):
        """See the base class for documentation
        
        @raise ConfigurationError: if the confidence function returns a value
            outside [0, 1]
        """
        ret_dict = super(ExplicitSubjectObjectRule, self)\
            .get_additional_instance_kwargs(ds_arg1, ds_arg2)
        
        # call the user-defined confidence method
        expectancy = self.expectancy(ds_arg1, ds_arg2)
        
        if not (MIN_EXPECTANCY <= expectancy <= MAX_EXPECTANCY):
            raise ConfigurationError(
                message=("The rule '%s' has expectancy %f, for the" + \
                    "  pair (%s, %s). Should be between 0 and 1.") % \
                        (self.name, expectancy, ds_arg1, ds_arg2),
                recommender=self.recommender,
                parameter_name="Recommender.rules",
                parameter_value=self.recommender.rules
            )
        
        ret_dict[EXPECTANCY_KWARG_NAME] = expectancy
        return ret_dict        

    @classmethod
    def _order_in_pair(cls, dn_arg1, dn_arg2, ds_arg1, ds_arg2):
        return PredictedRelationship._order_in_pair(dn_arg1, dn_arg2, ds_arg1, ds_arg2)
        
class _WeightedRelationship(BaseRelationship):
    """A class representing a relationship with a weight."""

    DefinitionClass = RuleRelationshipDefinition
    """The model class used for representing the definition of the 
    rule/relationship
    """  
    
    def __init__(self, name, is_positive, weight, condition=None, description=None, generator=None):
        """The constructor."""
        
        super(_WeightedRelationship, self).__init__(name, condition, description, generator)
        
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
                recommender=self.recommender,
                parameter_name="Recommender.rules or Recommender.relationships",
                parameter_value=(self.recommender.rules, self.recommender.relationships)
            )
        
        ret_dict['weight'] = self.weight
        ret_dict["relationship_type"] = self.relationship_type      
        
        return ret_dict
        
  
        

class SubjectObjectRelationship(_WeightedRelationship):
    """A class for representing subject-object preference for recommendation"""
    
    relationship_type = RELATIONSHIP_TYPE_SUBJECT_OBJECT
    """The type of the relationship S-O""" 

    @classmethod
    def _order_in_pair(cls, dn_arg1, dn_arg2, ds_arg1, ds_arg2):
        return PredictedRelationship._order_in_pair(dn_arg1, dn_arg2, ds_arg1, ds_arg2)

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
    
    def __init__(self, name, is_positive, weight, confidence, condition=None, description=None, generator=None):
        """The constructor.""" 

        super(_BaseRule, self).__init__(name, condition, is_positive, weight, description, generator)
        
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
        
        # call the user-defined confidence method
        confidence = self.confidence(ds_arg1, ds_arg2)
        
        if not (MIN_CONFIDENCE <= confidence <= MAX_CONFIDENCE):
            raise ConfigurationError(
                message=("The rule '%s' has a confidence %f, for the" + \
                    "  pair (%s, %s). Should be between 0 and 1.") % \
                        (self.name, confidence, ds_arg1, ds_arg2),
                recommender=self.recommender,
                parameter_name="Recommender.rules",
                parameter_value=self.recommender.rules
            )
        
        ret_dict[CONFIDENCE_KWARG_NAME] = confidence
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

    @classmethod
    def _order_in_pair(cls, dn_arg1, dn_arg2, ds_arg1, ds_arg2):
        return PredictedRelationship._order_in_pair(dn_arg1, dn_arg2, ds_arg1, ds_arg2)
        
class SubjectObjectSimilarityRule(_SimilarityRelationship):
    """A class used only when subject domain equals object domain. 
    For representing inter-entity rule.
    """
    
    relationship_type = RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT
    """The type of the relationship SO-SO"""

   
