"""A trivial algorithm returning what it has"""

from base import BaseAlgorithm
from unresyst.models.abstractor import RelationshipInstance, \
    PredictedRelationshipDefinition
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
            
    def get_recommendations(self, recommender_model, dn_subject, count, expectancy_limit, remove_predicted):
        """See the base class for the documentation.
                
        Here - Handle remove_predicted and expectancy_limit, return the predictions 
        we have. 
                
        """  
        if remove_predicted:
            
            # create kwargs to exclude already liked objects
            #
            
            # get objects that are already liked
            #
            qs_predicted = RelationshipInstance.filter_predicted(recommender_model)            

            # get ids of subjectobjects where dn_subject appears
            predicted_obj_ids = qs_predicted.filter( 
                subject_object1=dn_subject).values_list('subject_object2__pk', flat=True)
            
            # construct the arguments to the exclude method.
            exclude_args = {
                # the ones that have the predicted def
                'subject_object2__pk__in': predicted_obj_ids,
            }
                            
        else:
            exclude_args = {}            
        
        # get the recommendations ordered by the expectancy from the largest
        recommendations = RelationshipPredictionInstance.objects\
                            .filter(
                                subject_object1=dn_subject,
                                recommender=recommender_model, 
                                expectancy__gt=expectancy_limit)\
                            .exclude(**exclude_args)\
                            .distinct()\
                            .order_by('-expectancy')
        
        return list(recommendations[:count])                                                    
        

