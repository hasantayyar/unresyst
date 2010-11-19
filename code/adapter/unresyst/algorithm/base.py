"""The base abstract class for all recommender algorithms."""

class BaseAlgorithm(object):
    """The interface provided to the other packages. The methods in the interface
    are implemented by the subclasses"""
    
    # Build phase:
    #
    
    @classmethod
    def build(cls, recommender):
        """Build the recommender model, so that the given relationship can be
        predicted easily.
        """
        pass
    
    
    # Recommend phase:
    #
    
    @classmethod
    def get_relationship_prediction(cls, recommender, dn_subject, dn_object):
        """Get the prediction of the appearance of the predicted_relationship.
        
        @rtype: float
        @return: the probability of appearance of the predict_relationship
        """
        pass

        
    @classmethod
    def get_recommendations(cls, recommender, dn_subject):
        """Get the recommendations for the given subject
        
        @rtype: a list of SubjectObjects
        @return: the objects recommended to the subject
        """
        pass

    # Update phase:
    #         
    
    def update(recommender, aggregated_changes):
        """Update the recommender algorithm structures according to the changes
        in the aggregated relationships.
        
        """