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
        
        @rtype: float
        @return: The probability of the predicted relationship between the subject and
            the object.
        """
        pass
        
    @classmethod
    def get_recommendations(cls, subject, count=None):
        """Get recommendations for the given subject.
        
        @rtype: a list of objects
        @return: subject's recommended objects.
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
    
    relationships = None
    """Relationships among the subjects and objects in the domain"""
        
    rules = None
    """Rules that can be applied to the domain"""
    
    # Class configuration - the behaviour of the layers below the recommender
    # Empty, will be overriden by the Recommender class
    #
    
    Abstractor = None
    """The class that will be used for the abstractor level. Can be 
    overriden in suclasses"""
    
    Aggregator = None
    """The class that will be used for the aggregator level. Can be 
    overriden in suclasses"""
    
    Algorithm = None
    """The class that will be used for the algorithm level. Can be 
    overriden in suclasses"""
    

    
    #TODO jeste by to chtelo nejake settings, co to ma delat, kdyz se ptam na subject object pair, ktery uz mezi sebou ma predicted_relationship
