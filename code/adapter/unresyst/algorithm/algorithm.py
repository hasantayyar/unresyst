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
        
        # if subjects==objects
        if recommender_model.are_subjects_objects:

            # take similar on both sides
            cls._build_similar_subjectobjects(recommender_model)

        else:
        
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
        in predicted_relationship - that's a content-based recommender
        """   
        
        cls._build_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_SUBJECT)
    
    @classmethod        
    def _build_similar_subjects(cls, recommender_model):
        """Create predictions by adding objects that similar subjects liked
        - that's collaborative filtering
        """                
        
        cls._build_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_OBJECT)


    @classmethod
    def _build_similar_subjectobjects(cls, recommender_model):
        """Create predictions based on similarity for recommenders where 
        subjects==objects
        """
        
        # firstly the normal direction
        cls._build_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_SUBJECTOBJECT,
                reverse=False)
        
        # secondly the opposite
        cls._build_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_SUBJECTOBJECT,
                reverse=True)


    SIMILARITY_RELATIONSHIP_TYPES = {
        ENTITY_TYPE_SUBJECT: RELATIONSHIP_TYPE_OBJECT_OBJECT,
        ENTITY_TYPE_OBJECT: RELATIONSHIP_TYPE_SUBJECT_SUBJECT,
        ENTITY_TYPE_SUBJECTOBJECT: RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT
    }            
    """Dictionary entity type: relationship entity type.
    Key is the entity type where the traversing for similarity starts, value
    is the relationship type that should be traversed for similarity.
    """
    
    @classmethod
    def _build_similar_entities(cls, recommender_model, start_entity_type, reverse=False):
        """Create predictions from start_entity_type objects, looking for 
        similar entities in end_entity_type
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the model the for which the predictions
            should be built

        @type start_entity_type: str
        @param start_entity_type: the entity type, where to start searching for
            similar entities. E.g. if start_entity_type is 'S', similar 'O' 
            will be added to predictions to each 'S'.

        @type reverse: bool
        @param reverse: relevant only if start_entity_type=='SO', indicates 
            whether the relationships will be traversed in the reverse order.            
        """            
        
        # get the predictions for this recommender
        qs_predictions = RelationshipPredictionInstance.objects.filter(
                            recommender=recommender_model)
        
        # go through the predicted relationship instances 
        # (objects that subjects liked)
        qs_pred_rel_instances = RelationshipInstance.filter_predicted(recommender_model)        
        
        
        for pred_inst in qs_pred_rel_instances.iterator():

            # get the subject and object from the relationship instance
            start, fin = (pred_inst.subject_object1, pred_inst.subject_object2) \
                if pred_inst.subject_object1.entity_type == start_entity_type \
                else (pred_inst.subject_object2, pred_inst.subject_object1)
            
            # if they are subjectobjects and reversed swap them
            if start_entity_type == ENTITY_TYPE_SUBJECTOBJECT and reverse:
                start, fin = fin, start
            
            similarity_relationship_type = cls.SIMILARITY_RELATIONSHIP_TYPES[start_entity_type]
                
            # get objects similar to obj (whole relationships)
            qs_similar_rels = AggregatedRelationshipInstance\
                .get_relationships(fin)\
                .filter(relationship_type=similarity_relationship_type)
            
            # go through them 
            for similar_rel in qs_similar_rels.iterator():
            
                # get the object similar to obj from the relationship
                similar_fin = similar_rel.get_related(fin)

                # find out whether there exists a prediction for the pair
                qs_pair_predictions = RelationshipPredictionInstance\
                                        .filter_relationships(
                                            object1=start,
                                            object2=similar_fin,
                                            queryset=qs_predictions)

                # if exists, keep it there, ignore
                if qs_pair_predictions.exists():
                    continue

                # if not, create it with the attributes of the similarity 
                # relationship instance
                prediction = RelationshipPredictionInstance(
                            subject_object1=start,
                            subject_object2=similar_fin,
                            description=similar_rel.description,
                            expectancy=similar_rel.expectancy,
                            recommender=recommender_model)
                            
                prediction.save()                                 

        
    @classmethod        
    def _build_remove_predicted(cls, recommender_model):
        """Make zero instances that are already in the predicted_relationship.
        """
        
        # go through the predicted relationship instances, save with zero 
        # expectancy
        
        # get the predicted relationship instances
        qs_pred_rel_instances = RelationshipInstance.filter_predicted(recommender_model)

        # get the predictions for this recommender
        qs_predictions = RelationshipPredictionInstance.objects.filter(
                            recommender=recommender_model)
        
        for pred_rel_inst in qs_pred_rel_instances.iterator():

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
        
        
        
