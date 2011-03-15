"""The main classes of the algorithm package"""

from django.db.models import Q
from django.db.models import Avg

from base import BaseAlgorithm
from unresyst.constants import *
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance
from unresyst.models.aggregator import AggregatedRelationshipInstance
from unresyst.models.algorithm import RelationshipPredictionInstance
from unresyst.models.common import SubjectObject
from unresyst.recommender.rules import BaseRelationship

class Algorithm(BaseAlgorithm):
    """The original deprecated implementation mixing combinator, compilator and algorithm. 
    
    A simple implementation of a recommender algorithm.
    
    The remove_predicted_from_recommendations is implemented by adding a zero
    prediction for all pairs in predicted relationship. 
    
    The get_recommendation function returns only recommendations with expectancy
    above zero or the expectancy_limit.
    """
    
    N_NEIGHBOURHOOD = 10
    """The maximum size of the neighbourhood, from which the similar items are taken"""

    # Build phase:
    #
    
    def build(self, recommender_model):
        """Build the recommender - create the instances of the 
        RelationshipPredictionInstance model where there is some simple 
        prediction available. Where there isn't, leave it.
        """                        



    # Recommend phase:
    #


    def get_relationship_prediction(self, recommender_model, dn_subject, dn_object, remove_predicted):
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

                return self._get_already_in_relatinship_prediction(
                    recommender_model=recommender_model,
                    predicted_relationship=predicted)
            
        
        # filter the predictions for recommender
        qs_rec_pred = RelationshipPredictionInstance.objects.filter(
                        recommender=recommender_model)

        # filter the predictions for the given pair                        
        qs_pred = RelationshipPredictionInstance.filter_relationships(
                        object1=dn_subject,
                        object2=dn_object,
                        queryset=qs_rec_pred)        
                
        # if available return it
        if qs_pred:                   
            assert len(qs_pred) == 1
            return qs_pred[0]
        
        # if it's not available, maybe it wasn't in the N_NEIGHBOURHOOD, 
        # so try finding it in aggregates        
        so1, so2 = BaseRelationship.order_arguments(dn_subject, dn_object)

        # the Subject-object aggregate (just in case it hasn't been built)                
        qs_rels = AggregatedRelationshipInstance.objects.filter(
                    subject_object1=so1,
                    subject_object2=so2,
                    recommender=recommender_model)
        
        # if found return it
        if qs_rels:
            assert len(qs_rels) == 1

            pred = RelationshipPredictionInstance(
                    subject_object1=dn_subject,
                    subject_object2=dn_object,
                    description=qs_rels[0].description,
                    recommender=recommender_model,
                    expectancy=qs_rels[0].expectancy
                )
            pred.save()
            return pred

        # the definition of the predicted relationship
        d = PredictedRelationshipDefinition.objects.get(recommender=recommender_model)
        
        # try finding the similar entity to the one liked by so1
        # content-based                
        
        # get similarities starting the traverse with the similarity.
        qs_sim1 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model)\
            .filter(
                Q(
                    # take so2 as stable - in the subject_object2 position of the similarity
                    subject_object2=so2,
                    
                    # traverse from the other object in similarity (subject_object1) through
                    # the relationship instance, its subject (subject_object1) must be so1
                    subject_object1__relationshipinstance_relationships2__subject_object1=so1,
                    
                    # the relationship instance definition must be the predicted relationship def
                    subject_object1__relationshipinstance_relationships2__definition=d) | \
                Q(  
                    # take so2 as stable again, now in the subject_object1 position of the similarity
                    subject_object1=so2, 
                    
                    # traverse from the other through relationship to so1
                    subject_object2__relationshipinstance_relationships2__subject_object1=so1,
                    
                    # the definition again must be the predicted
                    subject_object2__relationshipinstance_relationships2__definition=d))

        # if found return
        if qs_sim1:

            # if found return the average TODO nejak jinak
            avg = qs_sim1.aggregate(Avg('expectancy'))

            pred = RelationshipPredictionInstance(
                    subject_object1=dn_subject,
                    subject_object2=dn_object,
                    description=qs_sim1[0].description,
                    recommender=recommender_model,
                    expectancy=avg['expectancy__avg']
                )
            pred.save()
            return pred                    

        
        # try finding the similar entity (user) to entity that liked so2
        # cf
        qs_sim2 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model)\
            .filter(
                Q(
                    # take so1 as stable - in the subject_object2 position of the similarity
                    subject_object2=so1,
                    
                    # traverse from the other object in similarity (subject_object1) through
                    # the relationship instance, its object (subject_object2) must be so2
                    subject_object1__relationshipinstance_relationships1__subject_object2=so2,
                    
                    # the relationship instance definition must be the predicted relationship def
                    subject_object1__relationshipinstance_relationships1__definition=d) | \
                Q(  
                    # take so1 as stable again, now in the subject_object1 position of the similarity
                    subject_object1=so1, 
                    
                    # traverse from the other through relationship to so2
                    subject_object2__relationshipinstance_relationships1__subject_object2=so2,
                    
                    # the definition again must be the predicted
                    subject_object2__relationshipinstance_relationships1__definition=d))

        # if found return the average TODO nejak jinak
        if qs_sim2:
            avg = qs_sim2.aggregate(Avg('expectancy'))
            
            pred = RelationshipPredictionInstance(
                    subject_object1=dn_subject,
                    subject_object2=dn_object,
                    description=qs_sim2[0].description,
                    recommender=recommender_model,
                    expectancy=avg['expectancy__avg']
                )
            pred.save()

            return pred                    
        
        
        # return the uncertain
        return self._get_uncertain_prediction(
                recommender_model=recommender_model, 
                dn_subject=dn_subject, 
                dn_object=dn_object
            )
        
    @classmethod
    def get_recommendations(self, recommender_model, dn_subject, count, expectancy_limit, remove_predicted):
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
                pred = self._get_uncertain_prediction(recommender_model, dn_subject, obj)
                uncertain_preds.append(pred)

            return list(positive_preds) + uncertain_preds + list(negative_preds)

        # apply the limit for count
        return list(recommendations[:count])                         
            



class PredictOnlyAlgorithm(Algorithm):
    """An algorithm that doesn't need to be built, performs only predictions."""
    
    @classmethod
    def build(self, recommender_model):
        """Do nothing"""
        return

    @classmethod
    def get_recommendations(self, recommender_model, dn_subject, count, expectancy_limit, remove_predicted):    
        """Raise an error"""
        raise NotImplementedError()    

