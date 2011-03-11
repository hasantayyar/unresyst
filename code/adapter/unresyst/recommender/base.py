"""Module containing the definition of BaseRecommender: the base class 
for user-defined recommenders.
"""

from unresyst.constants import *

class BaseRecommender(object):
    """The base class for all recommenders.
    
    Defines and the interface of the recommender. All methods and data fields
    are empty.
    """

    # Methods:
    #
    #

    # Build phase:
    #         
    @classmethod
    def build(cls):
        """Build the recommender. Process all the rules and relationships 
        in order to be able to provide recommendations.
        """
        pass
    
    # Recommend phase:
    #
    
    @classmethod        
    def predict_relationship(cls, subject, object_):    
        """Get the prediction of the given relationship type between the subject
        and the object. 
        
        @type subject: domain specific subject
        @param subject: the subject
        
        @type object_: domain specific object
        @param object_: the object
        
        @rtype: RelationshipPrediction
        @return: An instance representing the prediction of the relationship 
            between the subject and the object, containing the estimated 
            probability and explanation. If the prediction isn't known, returns
            an prediction with expectancy 0.5 and empty explanation
        
        @raise InvalidParameterError: if the given subject or object doesn't 
            have a domain neutral representation in the unresyst database. 
            Either the recommender hasn't been built or the subject/object was
            added later without updating the recommender.
        """
        pass
        
    @classmethod
    def get_recommendations(cls, subject, count=None):
        """Get recommendations for the given subject.

        @type subject: domain specific subject
        @param subject: the subject
                
        @type count: int
        @param count: a maximum number of objects to be recommended, if not given,
            the default_recommendation_count from the recommender class is used.
        
        @rtype: list of RelationshipPrediction
        @return: An instance representing the prediction of the relationship 
            between the subject and the object, containing the estimated 
            probability and explanation. If the prediction isn't known, returns
            an prediction with expectancy 0.5 and empty explanation

        @raise InvalidParameterError: if the given subject doesn't 
            have a domain neutral representation in the unresyst database. 
            Either the recommender hasn't been built or the subject was
            added later without updating the recommender.        
        """
        pass
 
        
    # Update phase:
    #  
    @classmethod       
    def add_subject(cls, subject):
        """Add subject to the recommender."""
        pass

    @classmethod
    def add_object(cls, object_):
        """Add object to the recommender."""
        pass

    @classmethod
    def update_subject(cls, subject):
        """Update the subject in the recommender, including its relationships
        and applied rules"""
        pass


    @classmethod    
    def update_object(cls, object_):
        """Update the object in the recommender, including its relationships
        and applied rules"""
        pass


    @classmethod
    def remove_subject(cls, subject):
        """Remove the subject from the recommender, including its relationships
        and applied rules"""
        pass


    @classmethod    
    def remove_object(cls, object_):
        """Remove the object from the recommender, including its relationships
        and applied rules"""
        pass      
                        
        
        
    # Domain specific data. empty, will be overriden in the domain specific recommender
    #

    name = ""
    """The name of the recommender"""
    
    subjects = None
    """The objects to who the recommender will recommend.
    Requires the following interface:
    on subjects manager:
     - iterator(): get an iterator on the collection
     - all(): get all sujbects
     - get(id=..) get the object with the given id
    queryset:
     - exists(): is there something in the queryset?
    on each subject instance:
     - id: an integer id of the subject    
     - __unicode__(): printable string
    """
    
    objects = None
    """The objects that will be recommended.""" 

    predicted_relationship = None
    """The relationship that will be predicted"""
    
    relationships = ()
    """Relationships among the subjects and objects in the domain"""
        
    rules = ()
    """Rules that can be applied to the domain"""
    
    cluster_sets = ()
    """Clusters to which subjects and objects can be divided"""
    
    biases = ()
    """Bias - predisposition of subjects/objects to be in the predicted_relationship"""

    random_recommendation_description = None
    """The description that will be used as a description 
    to random recommendations."""

    # Auxiliary class attributes
    _recommender_model = None
    """The database model instance belonging to the class"""
        
    # Class configuration - the behaviour of the layers below the recommender
    # Empty, will be overriden by the Recommender class
    #
    
    abstractor = None
    """The class that will be used for the abstractor level. Can be 
    overriden in subclasses"""    
    
    algorithm = None
    """The class that will be used for the algorithm level. Can be 
    overriden in subclasses"""
        
    remove_predicted_from_recommendations = None
    """Should the instances of the predicted_relationship be removed from
    recommendation list?
    """
    
    recommendation_expectancy_limit = None
    """The limit for expectancy above which the objects can be recommended.
    If not none, only objects with expectancy above the limit are recommended.
    A reasonable limit is 0.5 - the recommendations then don't include random 
    objects.
    """
    
    verbose_build = None
    """Should messages be printed during the build?"""
    
