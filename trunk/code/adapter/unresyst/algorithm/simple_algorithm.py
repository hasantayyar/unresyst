"""A trivial algorithm returning what it has"""

from base import BaseAlgorithm
from unresyst.models.abstractor import RelationshipInstance
from unresyst.models.algorithm import RelationshipPredictionInstance

class SimpleAlgorithm(BaseAlgorithm):
    
    # Build phase:
    #
    
    def build(cls, recommender_model):    
        """Do nothing"""
        return

    # Recommend phase:
    #
    
    def get_relationship_prediction(self, recommender_model, dn_subject, dn_object, remove_predicted):
        """See the base class for the documentation.
                
        Here - Handle remove_predicted, return the prediction if available, 
        if not, return uncertain. 
        """        

        # if predicted should be removed and the pair is in the predicted_rel, 
        # return the special expectancy value
        if remove_predicted:            
            # all predicted relationships
            qs_predicted = RelationshipInstance.filter_predicted(recommender_model)

            # the relationship between dn_subject and dn_object
            qs_predicted_rel = RelationshipInstance.filter_relationships(dn_subject, dn_object, queryset=qs_predicted)

            # if the prediction for the pair exists
            if qs_predicted_rel:
                
                # return the special expectancy value                
                assert len(qs_predicted_rel) == 1
                predicted = qs_predicted_rel[0]

                return self._get_already_in_relatinship_prediction(
                    recommender_model=recommender_model,
                    predicted_relationship=predicted)
        
        # if prediction available, return it
        # 
        
         # filter the predictions for recommender
        qs_pred = RelationshipPredictionInstance.objects.filter(
                        recommender=recommender_model,
                        subject_object1=dn_subject,
                        subject_object2=dn_object)
                
        # if available return it
        if qs_pred:                   
            assert len(qs_pred) == 1
            return qs_pred[0]                            
            
        # otherwise return the uncertain
        return self._get_uncertain_prediction(
                recommender_model=recommender_model, 
                dn_subject=dn_subject, 
                dn_object=dn_object
            )        
