"""Classes to represent bias of subjects and objects"""

from unresyst.constants import *

from unresyst.models.abstractor import BiasDefinition, BiasInstance
from unresyst.models.common import SubjectObject

class _BaseBias(object):
    """The base class for all bias clases"""
    
    entity_type = None
    """The entity type the bias is for s/o/so"""
    
    format_string = None
    """The format string appearing in the description"""
    
    def __init__(self, name, generator, is_positive, confidence, weight, description=None):
        """The constructor."""
        
        self.name = name
        """The name of the bias."""        
        
        self.description = description
        """A string describing the rule. It can contain placeholders for entities: 
        
         - %(subject)s for subject bias
         - %(object)s for object bias
         - %(subjectobject)s for subjectobject bias
        """
        
        self.is_positive = is_positive
        """Is the bias positive to the predicted relationship?"""
        
        self.generator = generator
        """A generator returning subjects/objects that are affected by the bias.
        """    
        
        self.weight = weight
        """A float number from [0, 1] representing the *static* weight of the bias
        It doesn't depend on the entity.
        """
        
        self.confidence = confidence
        """A float function giving values from [0, 1] representing the 
        the confidence of the bias of the entity. 
        It's dynamic, depends on the entity.
        """                
    
    def evaluate(self):
        """Crate bias definitions and the instances in the database.
        """
        
        if not (MIN_WEIGHT <= self.weight <= MAX_WEIGHT):
            raise ConfigurationError(
                message=("The bias '%s' provides weight %f," + 
                    " should be between 0 and 1. ."
                    ) % (self.name, self.weight),
                recommender=self.recommender,
                parameter_name="Recommender.biases",
                parameter_value=(self.recommender.biases)
            )
        
        recommender_model = self.recommender._get_recommender_model()

        # create the definition in the database
        definition = BiasDefinition.objects.create(
            name=self.name,
            recommender=recommender_model,
            entity_type=self.entity_type,
            weight=self.weight,
            is_positive=self.is_positive
        )        
        
        # go through the affected entities create bias instances
        #        
        for ds_entity in self.generator():
                                    
            # convert the entity to universal
            dn_entity = SubjectObject.get_domain_neutral_entity(
                domain_specific_entity=ds_entity, 
                entity_type=self.entity_type, 
                recommender=recommender_model)
            
            # count the confidence by the provided function    
            confidence = self.confidence(ds_entity)                            
                
            # if confidence invalid through an error
            if not (MIN_CONFIDENCE <= confidence <= MAX_CONFIDENCE):
                raise ConfigurationError(
                    message=("The bias '%s' provides confidence %f," + 
                        " should be between 0 and 1. "
                        ) % (self.name, confidence),
                    recommender=self.recommender,
                    parameter_name="Recommender.biases",
                    parameter_value=(self.recommender.biases)
                )
            
            # fill the description
            description = self.description % {self.format_string: dn_entity.name}
                
            # create the instance
            BiasInstance.objects.create(
                subject_object=dn_entity,
                confidence=confidence,
                definition=definition,
                description=description
            )                
                        
class SubjectBias(_BaseBias):

    entity_type = ENTITY_TYPE_SUBJECT
    
    format_string = FORMAT_STR_SUBJECT

    
class ObjectBias(_BaseBias):

    entity_type = ENTITY_TYPE_OBJECT
    
    format_string = FORMAT_STR_OBJECT

class SubjectObjectBias(_BaseBias):

    entity_type = ENTITY_TYPE_SUBJECTOBJECT
    
    format_string = FORMAT_STR_SUBJECTOBJECT
    
    
    
    
    
    
    
    
