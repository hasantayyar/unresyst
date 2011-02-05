"""The main classes of the algorithm package"""

from django.db.models import Q

from base import BaseAlgorithm
from unresyst.constants import *
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance
from unresyst.models.aggregator import AggregatedRelationshipInstance
from unresyst.models.algorithm import RelationshipPredictionInstance
from unresyst.models.common import SubjectObject

class SimpleAlgorithm(BaseAlgorithm):
    """A simple implementation of a recommender algorithm.
    
    The remove_predicted_from_recommendations is implemented by adding a zero
    prediction for all pairs in predicted relationship. 
    
    The get_recommendation function returns only recommendations with expectancy
    above zero or the expectancy_limit.
    """
    
    N_NEIGHBOURHOOD = 10
    """The maximum size of the neighbourhood, from which the similar items are taken"""

    # Build phase:
    #
    
    @classmethod
    def build(cls, recommender_model):
        """Build the recommender - create the instances of the 
        RelationshipPredictionInstance model where there is some simple 
        prediction available. Where there isn't, leave it.
        """
        print "Building aggregates."
        # for available aggregates create an instance with the aggregated result
        # 
        cls._build_aggregates(recommender_model)
        
        print "Done. Building similar objects."
        
        # if subjects == objects
        if recommender_model.are_subjects_objects:

            # take similar on both sides
            cls._build_similar_subjectobjects(recommender_model)

        else:
        
            # take similar to the ones we already have (content-based recommender)
            cls._build_similar_objects(recommender_model)
            print "Done. Building similar subjects."

            # take liked objects of similar users (almost collaborative filtering)
            cls._build_similar_subjects(recommender_model)                
        
        print "Done."
                

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

            # order the arguments as they should be    
            so1, so2 = cls._order_in_pair(aggr.subject_object1, aggr.subject_object2)

            prediction = RelationshipPredictionInstance(
                            subject_object1=so1,
                            subject_object2=so2,
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
    
    ORDERING = {
        ENTITY_TYPE_OBJECT: "subject_object1__pk",
        ENTITY_TYPE_SUBJECT: "subject_object2__pk",
        ENTITY_TYPE_SUBJECTOBJECT: "subject_object1__pk",
    }
    """Dictinary entity type (starting) - name of the attribute in PredictedRelationship, 
    that should be used for sorting"""
    
    
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

        ordering = cls.ORDERING[start_entity_type]
                   
        # go through the predicted relationship instances 
        # (objects that subjects liked)
        # ordered as needed
        qs_pred_rel_instances = RelationshipInstance\
            .filter_predicted(recommender_model)\
            .order_by(ordering)
        
        # the caching variable    
        last_fin = None       
        last_qs = None         
        
        print "Predicted relationship count: %d" % qs_pred_rel_instances.count()
        i = 0
        
        for pred_inst in qs_pred_rel_instances.iterator():
            
            i += 1
            # get the subject and object from the relationship instance
            start, fin = (pred_inst.subject_object1, pred_inst.subject_object2) \
                if pred_inst.subject_object1.entity_type == start_entity_type \
                else (pred_inst.subject_object2, pred_inst.subject_object1)
            
            # if they are subjectobjects and reversed swap them
            if start_entity_type == ENTITY_TYPE_SUBJECTOBJECT and reverse:
                start, fin = fin, start
            
            similarity_relationship_type = cls.SIMILARITY_RELATIONSHIP_TYPES[start_entity_type]
            
            # if the ending entity is the same as the last time, use the cached qs
            if last_fin == fin:
                qs_similar_rels = last_qs
            else:                
                # get objects similar to obj (whole relationships) - only N_NEIGHBOURHOOD highest
                qs_similar_rels = AggregatedRelationshipInstance\
                    .get_relationships(fin)\
                    .filter(relationship_type=similarity_relationship_type)\
                    .order_by('-expectancy')[:cls.N_NEIGHBOURHOOD]

            # keep it for the next time
            last_fin = fin
            last_qs = qs_similar_rels
            
            count = qs_similar_rels.count()
            if count and i % 1000 == 0:
                print "similar count: %d; relationships processed: %d" % (count, i)
            
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
                
                # order the arguments as they should be    
                so1, so2 = cls._order_in_pair(start, similar_fin)                    

                # if not, create it with the attributes of the similarity 
                # relationship instance
                prediction = RelationshipPredictionInstance(
                            subject_object1=so1,
                            subject_object2=so2,
                            description=similar_rel.description,
                            expectancy=similar_rel.expectancy,
                            recommender=recommender_model)
                            
                prediction.save()                                 
                    

    # Recommend phase:
    #

    @classmethod
    def get_relationship_prediction(cls, recommender_model, dn_subject, dn_object, remove_predicted):
        """See the base class for the documentation.
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

                return RelationshipPredictionInstance(
                    subject_object1=dn_subject,
                    subject_object2=dn_object,
                    description=predicted.description,
                    recommender=recommender_model,
                    expectancy=ALREADY_IN_REL_PREDICTION_VALUE
                ) 
            
        
        # filter the predictions for recommender
        qs_rec_pred = RelationshipPredictionInstance.objects.filter(
                        recommender=recommender_model)

        # filter the predictions for the given pair                        
        qs_pred = RelationshipPredictionInstance.filter_relationships(
                        object1=dn_subject,
                        object2=dn_object,
                        queryset=qs_rec_pred)        
        
        # if not available return the uncertain                        
        if not qs_pred:
            return cls._get_uncertain_prediction(
                recommender_model=recommender_model, 
                dn_subject=dn_subject, 
                dn_object=dn_object
            )
        
        # otherwise return the found one
        assert len(qs_pred) == 1

        return qs_pred[0]
        
    @classmethod
    def get_recommendations(cls, recommender_model, dn_subject, count, expectancy_limit, remove_predicted):
        """See the base class for documentation.
        """                
        
        # get the recommendations ordered by the expectancy from the largest
        recommendations = RelationshipPredictionInstance\
                            .get_relationships(obj=dn_subject)\
                            .filter(recommender=recommender_model, 
                                expectancy__gt=expectancy_limit)\
                            .order_by('-expectancy')                            
        
        # remove the predicted from the recommendations if it should be done        
        if remove_predicted:
            
            # get objects that are already liked
            #
                        
            qs_predicted = RelationshipInstance.filter_predicted(recommender_model)            

            # get ids of subjectobjects where dn_subject appears
            qs_predicted = qs_predicted.filter( 
                Q(subject_object1=dn_subject) | Q(subject_object2=dn_subject)           
            ).values_list('subject_object1__pk', 'subject_object2__pk')
            
            # flatten it and take only the objects
            import itertools                
            predicted_obj_ids = [i for i in itertools.chain(*qs_predicted) if i <> dn_subject.pk]            

            # remove the already liked objects
            #
            
            # if it is a subjectobject we have to take both places
            if dn_subject.entity_type == ENTITY_TYPE_SUBJECTOBJECT:
                recommendations = recommendations.exclude(
                    Q(subject_object1__id__in=predicted_obj_ids) 
                        | Q(subject_object2__id__in=predicted_obj_ids)
                )
            # otherwise one field is enough
            else:
                recommendations = recommendations.exclude(
                    subject_object2__id__in=predicted_obj_ids
                )
                    
        # if there should be more recommendations than we have and 
        # the expectancy limit is below the uncertain, add uncertain 
        # predictions
        if recommendations.count() < count \
            and expectancy_limit < UNCERTAIN_PREDICTION_VALUE:                       

            object_ent_type = ENTITY_TYPE_SUBJECTOBJECT \
                if recommender_model.are_subjects_objects \
                else ENTITY_TYPE_OBJECT            

            # all objects excluding the objects recommended to dn_subject
            # the last exclude is just for SO entity_type - we won't recommend 
            # subject to himself
            uncertain_objects = SubjectObject.objects\
                .filter(entity_type=object_ent_type, recommender=recommender_model)\
                .exclude(relationshippredictioninstance_relationships1__subject_object2=dn_subject)\
                .exclude(relationshippredictioninstance_relationships2__subject_object1=dn_subject)\
                .exclude(pk=dn_subject.pk)
            
            # if predicted should be removed remove them
            if remove_predicted:
                uncertain_objects = uncertain_objects.exclude(id__in=predicted_obj_ids)
            
            # divide the recommendations into groups exp => uncertain, exp < uncertain
            positive_preds = recommendations.filter(
                expectancy__gte=UNCERTAIN_PREDICTION_VALUE)
            negative_preds = recommendations.filter(
                expectancy__lt=UNCERTAIN_PREDICTION_VALUE)
            
            # how many non-positive recommendations we want
            required_count = count - positive_preds.count()
            uncertain_count = uncertain_objects.count()
            
            # if there're enough uncertains to fill the recommendations, 
            # clear the negative
            if uncertain_count >= required_count:
                uncertain_required_count = required_count
                negative_preds = []
            else:
                # otherwise we want all uncertains we have
                uncertain_required_count = uncertain_count

                negative_required_count = required_count - uncertain_count
                
                # and for the rest use negative - only those above limit
                negative_preds = negative_preds.filter(
                    expectancy__gt=expectancy_limit)[:negative_required_count]

            uncertain_preds = []
                
            # construct the uncertain recommendations
            for obj in uncertain_objects[:uncertain_required_count]:
                pred = cls._get_uncertain_prediction(recommender_model, dn_subject, obj)
                uncertain_preds.append(pred)

            return list(positive_preds) + uncertain_preds + list(negative_preds)

        # apply the limit for count
        return list(recommendations[:count])
                         
    @staticmethod
    def _get_uncertain_prediction(recommender_model, dn_subject, dn_object):
        """Get the prediction for a pair for which nothing is known"""
        
        return RelationshipPredictionInstance(
                subject_object1=dn_subject,
                subject_object2=dn_object,
                description=recommender_model.random_recommendation_description,
                recommender=recommender_model,
                expectancy=UNCERTAIN_PREDICTION_VALUE
            ) 
            
    @classmethod
    def _order_in_pair(cls, arg1, arg2):
        """Swap the arguments in the rule/relationships so that the first
        has a lower id than the second (for subjectobjects), or the subject
        is the first (for others)
        """
        # for subjectobject return ordered by pk
        if arg1.entity_type == ENTITY_TYPE_SUBJECTOBJECT:
            if arg2.pk < arg1.pk:
                return (arg2, arg1)
            return (arg1, arg2)
        # for others return subject first            
        if arg2.entity_type == ENTITY_TYPE_SUBJECT:
            return (arg2, arg1)
        return (arg1, arg2)


