"""Module containing the definition of BaseRecommender: the base class 
for user-defined recommenders.

Contents:
 - Recommender: the recommender for client subclassing
 - MetaRecommender: the metaclass for creating recommender classes
"""
from base import BaseRecommender
from predictions import RelationshipPrediction
from unresyst.constants import *
from unresyst.exceptions import ConfigurationError, InvalidParameterError, \
    RecommenderNotBuiltError
from unresyst.abstractor import BasicAbstractor 
from unresyst.aggregator import LinearAggregator
from unresyst.algorithm import SimpleAlgorithm
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel


class MetaRecommender(type):
    """The meta-class adding a reference to the class for the contained
    rules and relationships.
    """
    def __init__(cls, name, bases, dct):        
        """The class initializer.
        
        Adds the reference to the recommender class to all of the rules
        and relationships.
        
        Tries searching for the recommender model in the database.
        """
        
        super(MetaRecommender, cls).__init__(name, bases, dct)
        
        # add the recommender class to the predicted relationship
        if cls.predicted_relationship:       
            cls.predicted_relationship.recommender = cls
        
        # then to the rules
        if cls.rules:
            for rule in cls.rules:
                rule.recommender = cls
            
        # finally to the relationships
        if cls.relationships:
            for relationship in cls.relationships:
                relationship.recommender = cls        


class Recommender(BaseRecommender):
    """The base class for all user-defined recommenders.
    
    Implements the interface of the recommender. It doesn't hold any 
    domain specific data.
    
    Defines default behaviour assigning the classes for the layers. 
    
    The predicted relationship is ignored when building and updating the 
    recommender. If it's needed, one should create a rule/relationship 
    with the appropriate condition.
    
    The contained rules and relationships have to be included in only one
    recommender class. There can't be a rule/relationship instance 
    which is contained in two recommender classes.
    """
    __metaclass__ = MetaRecommender
    """A metaclass putting the reference to the recommender to all member
    rules and relationships.
    """        
    
    # Build phase:
    #
    
    @classmethod
    def build(cls):
        """For documentation, see the base class"""
        
        
        # validate the subclass data
        # 
        
        # Subjects, objects non-empty
        if not cls.subjects.all().exists():
            raise ConfigurationError(
                message="No subjects given",
                recommender=cls,
                parameter_name="Recommender.subjects",
                parameter_value=cls.subjects
            )
        
        if not cls.objects.all().exists():
            raise ConfigurationError(
                message="No objects given",
                recommender=cls,
                parameter_name="Recommender.objects",
                parameter_value=cls.objects
            )
                
                    
        # predicted relationship given
        if not cls.predicted_relationship:
            raise ConfigurationError(
                message="No predicted relationship given",
                recommender=cls,
                parameter_name="Recommender.predicted_relationship",
                parameter_value=cls.predicted_relationship
            )
        
        # rules and relationships don't have to be given

        # if the recommender with the given name exists, delete it,
        RecommenderModel.objects.filter(class_name=cls.__name__).delete()
                
        # create a new recommender and save it, keep it in the class
        recommender_model = RecommenderModel(
            class_name=cls.__name__,
            name=cls.name,
            is_built=False,
            are_subjects_objects=(cls.subjects == cls.objects),
            random_recommendation_description=cls.random_recommendation_description
        )        
        recommender_model.save() 
        
        # build the recommender model
        #
        #
        
        
        # Abstractor
        #
        
        # create the domain neutral representation for objects and subjects
        cls.Abstractor.create_subjectobjects(
            recommender_model=recommender_model,
            subjects=cls.subjects, 
            objects=cls.objects
        )
        
        # create the relationship instances for the predicted relationship
        cls.Abstractor.create_predicted_relationship_instances(           
            predicted_relationship=cls.predicted_relationship            
        )
        
        # create relationship instances between subjects/objects 
        cls.Abstractor.create_relationship_instances(
            relationships=cls.relationships
        )    
               
        # evaluate rules and make rule instances between the affected 
        # subjects/objects
        cls.Abstractor.create_rule_instances(rules=cls.rules)
        

        # Aggregator
        # 
        
        # aggregate the relationships and rules
        cls.Aggregator.aggregate(recommender_model=recommender_model)        
        
        # Algorithm
        #        
        # build the algorithm model from the aggregated relationships
        cls.Algorithm.build(
            recommender_model=recommender_model, 
            remove_predicted=cls.remove_predicted_from_recommendations
        )
        
        # mark the recommender as built, save it and keep it in the class
        recommender_model.is_built = True
        recommender_model.save()


    # Recommend phase:
    # 
    
    @classmethod        
    def predict_relationship(cls, subject, object_):
        """For documentation, see the base class"""        
        
        recommender_model = cls._get_recommender_model()
        # if the recommender isn't built raise an error
        if not recommender_model or not recommender_model.is_built:
            raise RecommenderNotBuiltError(
                message="Build the recommender prior to performing the " + \
                    "predict_relationship action.",
                recommender=cls
            )
                
        
        subject_ent_type = ENTITY_TYPE_SUBJECT \
                            if not recommender_model.are_subjects_objects \
                            else ENTITY_TYPE_SUBJECTOBJECT

        object_ent_type = ENTITY_TYPE_OBJECT \
                            if not recommender_model.are_subjects_objects \
                            else ENTITY_TYPE_SUBJECTOBJECT

        # get the domain neutral representations for the subject and object
        try:
            dn_subject = SubjectObject.get_domain_neutral_entity(
                domain_specific_entity=subject,
                entity_type=subject_ent_type,
                recommender=recommender_model
            )
        except SubjectObject.DoesNotExist, e:
            raise InvalidParameterError(
                message="The subject wasn't found in the recommender database." + \
                    "Try rebuilding the recommender. Exception: %s" % e,
                recommender=cls,
                parameter_name='subject', 
                parameter_value=subject)            

        try:                
            dn_object = SubjectObject.get_domain_neutral_entity(
                domain_specific_entity=object_,
                entity_type=object_ent_type,
                recommender=recommender_model
            )
        except SubjectObject.DoesNotExist, e:
            raise InvalidParameterError(
                message="The object wasn't found in the recommender database." + \
                    "Try rebuilding the recommender. Exception: %s" % e,
                recommender=cls,
                parameter_name='object_', 
                parameter_value=object_)     
        
        # get the prediction from the algorithm
        prediction_model = cls.Algorithm.get_relationship_prediction(
            recommender_model=recommender_model,
            dn_subject=dn_subject,
            dn_object=dn_object
        )
        
        # create and return the outer-world object
        prediction = RelationshipPrediction(
            subject=subject,
            object_=object_,
            expectancy=prediction_model.expectancy,
            explanation=prediction_model.description
        )            
        return prediction


    @classmethod
    def get_recommendations(cls, subject, count=None):        
        """For documentation, see the base class"""
        
        recommender_model = cls._get_recommender_model()
        
        # if the recommender isn't built raise an error
        if not recommender_model or not recommender_model.is_built:
            raise RecommenderNotBuiltError(
                message="Build the recommender prior to performing the " + \
                    "get_recommendations action.",
                recommender=cls
            )
        
        # if count wasn't given take the default one
        if not count:
            count = cls.default_recommendation_count
        
        subject_ent_type = ENTITY_TYPE_SUBJECT \
                            if not recommender_model.are_subjects_objects \
                            else ENTITY_TYPE_SUBJECTOBJECT
                            
        # convert the the subject to domain neutral
        try:
            dn_subject = SubjectObject.get_domain_neutral_entity(
                domain_specific_entity=subject,
                entity_type=subject_ent_type,
                recommender=recommender_model
            )
        except SubjectObject.DoesNotExist, e:
            raise InvalidParameterError(
                message="The subject wasn't found in the recommender database." + \
                    "Try rebuilding the recommender. Exception: %s" % e,
                recommender=cls,
                parameter_name='subject', 
                parameter_value=subject)  

        limit = cls.recommendation_expectancy_limit \
            if not cls.recommendation_expectancy_limit is None else 0

        # get the recommendations from the algorithm
        prediction_models = cls.Algorithm.get_recommendations(
            recommender_model=recommender_model,
            dn_subject=dn_subject,
            count=count,
            expectancy_limit=limit
        )
        
        recommendations = []
        
        # go through the obtained predictions
        for pred_model in prediction_models:

            # obtain the object from the prediction
            dn_object = pred_model.get_related(dn_subject)
            
            # get its domain specific representation
            object_ = dn_object.get_domain_specific_entity(entity_manager=cls.objects)
                        
            # create the outer-world object
            prediction = RelationshipPrediction(
                subject=subject,
                object_=object_,
                expectancy=pred_model.expectancy,
                explanation=pred_model.description
            )            
            
            recommendations.append(prediction)

        return recommendations


    # Update phase:
    # 
    @classmethod
    def add_subject(cls, subject):
        """For documentation, see the base class"""
        
        # add the object to abstractor rule/relationship instances, 
        # see what has changed
        instance_changes = cls.Abstractor.add_subject(
            recommender=cls.__name__,
            subject=subject
        )
        
        # let the Aggregator update the aggregates
        aggregated_changes = cls.Aggregator.update(
            recommender=cls.__name__,
            instance_changes=instance_changes
        )
        
        # let the Algorithm update its structures
        cls.Algorithm.update(
            recommender=cls.__name__,
            aggregated_changes=aggregated_changes
        )


    @classmethod
    def add_object(cls, object_):
        """For documentation, see the base class"""
        
        # add the object to abstractor rule/relationship instances
        # see what has changed
        instance_changes = cls.Abstractor.add_object(
            recommender=cls.__name__,
            object_=object_
        )
        # pak nejak podobne - asi na to udelat fci. 

    @classmethod
    def update_subject(cls, subject):
        """For documentation, see the base class"""

        # update the subject in abstractor rule/relationship instances
        # see what has changed
        instance_changes = cls.Abstractor.update_subject(
            recommender=cls.__name__,
            subject=subject
        )
        # pak nejak podobne - asi na to udelat fci.


    @classmethod    
    def update_object(cls, object_):
        """For documentation, see the base class"""

        # update the object in abstractor rule/relationship instances
        # see what has changed
        instance_changes = cls.Abstractor.update_object(
            recommender=cls.__name__,
            object_=object_
        )
        # pak nejak podobne - asi na to udelat fci.      
        
    @classmethod
    def remove_subject(cls, subject):
        """For documentation, see the base class"""

        # remove the subject from abstractor rule/relationship instances
        # see what has changed
        instance_changes = cls.Abstractor.remove_subject(
            recommender=cls.__name__,
            subject=subject
        )
        # pak nejak podobne - asi na to udelat fci.


    @classmethod    
    def remove_object(cls, object_):
        """For documentation, see the base class"""

        # update the object in abstractor rule/relationship instances
        # see what has changed
        instance_changes = cls.Abstractor.remove_object(
            recommender=cls.__name__,
            object_=object_
        )
        # pak nejak podobne - asi na to udelat fci.                 
        


    # Class configuration - the behaviour of the layers below the recommender
    # Can be overriden in user defined subclasses
    
    Abstractor = BasicAbstractor
    """The class that will be used for the abstractor level. Can be 
    overriden in suclasses"""
    
    Aggregator = LinearAggregator  
    """The class that will be used for the aggregator level. Can be 
    overriden in suclasses"""
    
    Algorithm = SimpleAlgorithm
    """The class that will be used for the algorithm level. Can be 
    overriden in suclasses"""
    
    default_recommendation_count = DEFAULT_RECOMMENDATION_COUNT
    """The defaul count of the obtained recommended objects"""
    
    remove_predicted_from_recommendations = True
    """The entity pairs that already have the predicted_relationship
    between them, will be removed from recommendation list.
    """
    
    random_recommendation_description = "A random object"
    """The description for random recommendations Can be overriden in
    subclass"""
    
    # Auxiliary methods - not to be used from outside the application
    #    
    @classmethod
    def _get_recommender_model(cls):
        """Get the recommender model belonging to the class"""
        
        # can't be caching 'cause database can die out without notifying the 
        # if it's already saved, return it
        #if cls._recommender_model:
        #    return cls._recommender_model
        
        # otherwise try finding it in database            
        models = RecommenderModel.objects.filter(class_name=cls.__name__)
        
        # if the recommender was found, assign it to the class and return it
        if models:            
            assert len(models) == 1
            cls._recommender_model = models[0]
            return cls._recommender_model
        
        # if not return None
        return None            
    
    @classmethod
    def _get_entity_manager(cls, entity_type):
        """Get the manager from the recommender for the given entity type.
        
        @type entity_type: str
        @param entity_type: the type of the entity 'S'/'O'/'SO'
        
        @rtype: django.db.models.manager.Manager
        @return: the manager over the domain specific entities.
        
        @raise KeyError: when the entity_type is invalid 
        """
        
        manager_dict = {
            ENTITY_TYPE_SUBJECT: cls.subjects,
            ENTITY_TYPE_OBJECT: cls.objects,            
            ENTITY_TYPE_SUBJECTOBJECT: cls.objects # or sujbects if you care
        }
        
        return manager_dict[entity_type]
