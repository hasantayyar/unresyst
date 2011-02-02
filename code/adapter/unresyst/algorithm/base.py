"""The base abstract class for all recommender algorithms."""

class BaseAlgorithm(object):
    """The interface provided to the other packages. The methods in the interface
    are implemented by the subclasses"""
    
    # Build phase:
    #
    
    @classmethod
    def build(cls, recommender_model):
        """Build the recommender, so that the given relationship can be
        predicted easily.
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender whose instances should
            be aggregated. 

        """
        pass
    
    
    # Recommend phase:
    #
    
    @classmethod
    def get_relationship_prediction(cls, recommender_model, dn_subject, dn_object, remove_predicted):
        """Get the prediction of the appearance of the predicted_relationship.

        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender whose instances should
            be aggregated.         
        
        @type dn_subject: models.common.SubjectObject
        @param dn_subject: the domain neutral subject
        
        @type dn_object: models.common.SubjectObject
        @param dn_object: the domain neutral object

        @type remove_predicted: bool
        @param remove_predicted: should pairs already having 
            predicted_relationship between them get the special expectancy value?
            
        @rtype: models.algorithm.RelationshipPredictionInstance
        @return: the model instance for the prediction 
        """
        pass

        
    @classmethod
    def get_recommendations(cls, recommender_model, dn_subject, count, expectancy_limit, remove_predicted):
        """Get the recommendations for the given subject

        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender whose instances should
            be aggregated. 

        @type dn_subject: models.common.SubjectObject
        @param dn_subject: the domain neutral subject

        @type count: int
        @param count: how many recommendations should be obtained
        
        @type expectancy_limit: float
        @param expectancy_limit: the lower limit for object expectancy, only
            objects with expectancy higher than limit are recommended.
        
        @type remove_predicted: bool
        @param remove_predicted: should pairs already having 
            predicted_relationship between them be removed from recommendations?
            
        @rtype: a list of models.algorithm.RelationshipPredictionInstance
        @return: the predictions of the objects recommended to the subject
        """
        pass

    # Update phase:
    #         
    
    def update(recommender, aggregated_changes):
        """Update the recommender algorithm structures according to the changes
        in the aggregated relationships.
        
        """
