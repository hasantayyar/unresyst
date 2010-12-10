"""Module containing the definition of BaseRecommender: the base class 
for user-defined recommenders.
"""
from base import BaseRecommender
from unresyst.constants import *
from unresyst.exceptions import ConfigurationError
from unresyst.abstractor import BasicAbstractor 
from unresyst.aggregator import LinearAggregator
from unresyst.algorithm import DummyAlgorithm
from unresyst.models.common import Recommender as RecommenderModel

class Recommender(BaseRecommender):
    """The base class for all user-defined recommenders.
    
    Implements the interface of the recommender. It doesn't hold any 
    domain specific data.
    
    Defines default behaviour assigning the classes for the layers. 
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
                parameter_name="Recommender.subjects",
                parameter_value=cls.subjects
            )
        
        if not cls.objects.all().exists():
            raise ConfigurationError(
                message="No objects given",
                parameter_name="Recommender.objects",
                parameter_value=cls.objects
            )
                
                    
        # predicted relationship given
        if not cls.predicted_relationship:
            raise ConfigurationError(
                message="No predicted relationship given",
                parameter_name="Recommender.predicted_relationship",
                parameter_value=cls.predicted_relationship
            )
        
        # rules and relationships don't have to be given

        # if the recommender with the given name doesn't exist, create it,
        # if it does, find it
        recommender, created = RecommenderModel.objects.get_or_create(
                        class_name=cls.__name__,
                        defaults={"name": cls.name})
        
        # build the recommender model
        #
        #
        
        
        # Abstractor
        #
        
        # create the domain neutral representation for objects and subjects
        cls.Abstractor.create_subjectobjects(
            recommender=recommender,
            subjects=cls.subjects, 
            objects=cls.objects
        )
        
        # create the relationship instances for the predicted relationship
        cls.Abstractor.create_predicted_relationship_instances(
            recommender=cls.__name__,            
            predicted_relationship=cls.predicted_relationship            
        )
        
        # create relationship instances between subjects/objects 
        cls.Abstractor.create_relationship_instances(
            recommender=cls.__name__,
            relationships=cls.relationships
        )    
                
        # evaluate rules and make rule instances between the affected subjects/objects
        cls.Abstractor.create_rule_instances(
            recommender=cls.__name__,        
            rules=cls.rules
        )
        
        # Aggregator
        # 
        
        # aggregate the relationships and rules
        cls.Aggregator.aggregate(recommender=cls.__name__)        
        
        # Algorithm
        #
        
        # build the algorithm model from the aggregated relationships
        cls.Algorithm.build(recommender=cls.__name__)


    # Recommend phase:
    # 
    
    @classmethod        
    def predict_relationship(cls, subject, object_):
        """For documentation, see the base class"""

        # get the domain neutral representations for the subject and object
        dn_subject = cls.Abstractor.get_dn_subject(
            recommender=cls.__name__, 
            subject=subject
        )
        dn_object = cls.Abstractor.get_dn_object(
            recommender=cls.__name__, 
            object_=object_
        )
        
        # get the prediction from the algorithm
        return cls.Algorithm.get_relationship_prediction(
            recommender=cls.__name__,
            dn_subject=dn_subject,
            dn_object=dn_object
        )
    
    @classmethod
    def get_recommendations(cls, subject, count=None):        
        """For documentation, see the base class"""
        
        # if count wasn't given take the default one
        if not count:
            count = cls.default_recommendation_count
        
        # convert the the subject to domain neutral
        dn_subject = cls.Abstractor.get_dn_subject(
            recommender=cls.__name__, 
            subject=subject
        )
        
        # get the recommendations from the algorithm
        dn_objects = cls.Algorithm.get_recommendations(
            recommender=cls.__name__,
            dn_subject=dn_subject
        )
        
        # convert the object to domain specific
        return [cls.Abstractor.get_object(
                    recommender=cls.__name__,
                    dn_object=dn_object
                ) for dn_object in dn_objects]

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
    
    Algorithm = DummyAlgorithm
    """The class that will be used for the algorithm level. Can be 
    overriden in suclasses"""
    
    default_recommendation_count = DEFAULT_RECOMMENDATION_COUNT
    """The defaul count of the obtained recommended objects"""
