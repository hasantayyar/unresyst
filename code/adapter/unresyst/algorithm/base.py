"""The base abstract class for all recommender algorithms."""

class BaseAlgorithm(object):
    """The interface provided to the other packages. The methods in the interface
    are implemented by the subclasses"""
    
    def __init__(self, inner_algorithm=None):
        """The initializer"""
        
        self.inner_algorithm = inner_algorithm
        """The inner algorithm"""
        
    # Build phase:
    #
    
    def build(self, recommender_model):
        """Build the recommender, so that the given relationship can be
        predicted easily.
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender whose instances should
            be aggregated. 

        """
        if self.inner_algorithm:
            self.inner_algorithm.build(recommender_model=recommender_model)
    
    
    # Recommend phase:
    #
    
    def get_relationship_prediction(self, recommender_model, dn_subject, dn_object, remove_predicted):
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
        if self.inner_algorithm:
            return self.get_relationship_prediction(
                recommender_model=recommender_model, 
                dn_subject=dn_subject, 
                dn_object=dn_object, 
                remove_predicted=remove_predicted)

        
    def get_recommendations(self, recommender_model, dn_subject, count, expectancy_limit, remove_predicted):
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
        if self.inner_algorithm:
            return self.get_recommendations(
                recomender_model=recommender_model,
                dn_subject=dn_subject,
                count=count,
                expectancy_limit=expectancy_limit,
                remove_predicted=remove_predicted)

    # Update phase:
    #         
    
    def update(self, recommender, aggregated_changes):
        """Update the recommender algorithm structures according to the changes
        in the aggregated relationships.
        
        """
