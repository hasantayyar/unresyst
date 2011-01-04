"""The main classes of the algorithm package"""

from base import BaseAlgorithm
from unresyst.constants import *
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance
from unresyst.models.aggregator import AggregatedRelationshipInstance
from unresyst.models.algorithm import RelationshipPredictionInstance

class SimpleAlgorithm(BaseAlgorithm):
    """A simple implementation of a recommender algorithm"""

    # Build phase:
    #
    
    @classmethod
    def build(cls, recommender_model, remove_predicted):
        """Build the recommender - create the instances of the 
        RelationshipPredictionInstance model where there is some simple 
        prediction available. Where there isn't, leave it.
        """
        
        # for available aggregates create an instance with the aggregated result
        # 
        cls._build_aggregates(recommender_model)
        
        # take similar to the ones we already have (content-based recommender)
        cls._build_similar_objects(recommender_model)
        
        # take liked objects of similar users (almost collaborative filtering)
        cls._build_similar_subjects(recommender_model)                
        
        # remove the ones that are already in the predicted_relationship 
        # (if it should be done)
        if remove_predicted:
            cls._build_remove_predicted(recommender_model)
        

    @classmethod        
    def _build_aggregates(cls, recommender_model):
        """Create predictions from aggregates"""        
        
        # filter only S-O or SO-SO aggregates
        #
        rel_type = RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT \
            if recommender_model.are_subjects_objects else \
                RELATIONSHIP_TYPE_SUBJECT_OBJECT 
        
        qs_aggr = AggregatedRelationshipInstance.objects.filter(
                    recommender=recommender_model,
                    relationship_type=rel_type)

        # go through the aggregates, create predictions and save them
        for aggr in qs_aggr.iterator():

            prediction = RelationshipPredictionInstance(
                            subject_object1=aggr.subject_object1,
                            subject_object2=aggr.subject_object2,
                            description=aggr.description,
                            expectancy=aggr.expectancy,
                            recommender=recommender_model)
                            
            prediction.save()                            
                            

        
    @classmethod        
    def _build_similar_objects(cls, recommender_model):
        """Create predictions by adding objects similar to ones the objects
        liked - that's a content-based recommender
        """                
        
        # if exists, ignore

    @classmethod        
    def _build_similar_subjects(cls, recommender_model):
        """Create predictions by adding objects that similar subjects liked
        - that's collaborative filtering
        """                
        
        # if exists, ignore

        
    @classmethod        
    def _build_remove_predicted(cls, recommender_model):
        """Make zero instances that are already in the predicted_relationship.
        """
        
        # go through the predicted relationship instances, save with zero 
        # expectancy
        
        # get the predicted relationship definition
        pred_rel_def = PredictedRelationshipDefinition.objects.get(
                        recommender=recommender_model)

        # get the predicted relationship instances
        qs_pred_instances = RelationshipInstance.objects.filter(
                                definition=pred_rel_def)

        # get the predictions for this recommender
        qs_predictions = RelationshipPredictionInstance.objects.filter(
                            recommender=recommender_model)
        
        for pred_rel_inst in qs_pred_instances.iterator():

            # if the pair is already predicted somehow, zeroize it
            #                        
            
            # get pairs that are already in prediction
            pair_predictions = RelationshipPredictionInstance.filter_relationships(
                            object1=pred_rel_inst.subject_object1,
                            object2=pred_rel_inst.subject_object2,
                            queryset=qs_predictions)
            
            pred_count = pair_predictions.count()

            if pred_count > 0:
                # if the are multiple predictions for one recommender and pair, it's 
                # an internal error
                assert pred_count == 1
                
                prediction = pair_predictions[0]
                prediction.description = pred_rel_inst.description
                prediction.expectancy = 0
            else:                    
                # create and save the prediction with zero
                # use the description of the predicted relationship
                prediction = RelationshipPredictionInstance(
                                subject_object1=aggr.subject_object1,
                                subject_object2=aggr.subject_object2,
                                description=pred_rel_inst.description,
                                expectancy=0,
                                recommender=recommender_model)

            prediction.save()
        
        
        
