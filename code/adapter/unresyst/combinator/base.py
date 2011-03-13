"""Base classes for the combinator layer:
 - BaseCombinator
"""

from unresyst.models.abstractor import RelationshipInstance, RuleInstance, \
    ExplicitRuleInstance, PredictedRelationshipDefinition, ClusterMember
from unresyst.models.aggregator import AggregatedRelationshipInstance, AggregatedBiasInstance
from unresyst.models.algorithm import RelationshipPredictionInstance
from unresyst.constants import *

class BaseCombinator(object):
    """The empty base class defining the interface of all combinators."""
    
    DIVISOR = 3
    """A constant for dividing the relationship members that would otherwise be 
    too numerous"""
    
    def __init__(self):
        """The initializer"""
        
        self.top_bias_objects = None

    def _combine(self, combination_elements, ResultClass):
        """Combine the combination elements to produce an instance 
        of the ResultClass, filling in its expectancy and description.
        
        Overriden in subclasses

        @type combination_elements: a list of BaseCombinationElement
        @param combination_elements: the elements that should be combined

        @type ResultClass: class
        @param ResultClass: the class which instance will be returned
        
        @rtype: ResultClass
        @return: the combination class with filled expectancy and description
        """
        pass


    def combine_pair_similarities(self, combination_elements):
        """Aggregate similarities of the given pair S-S, O-O, or SO-SO. 
        
        @type combination_elements: a list of BaseCombinationElement
        @param combination_elements: the elements that should be combined        
            
        @rtype: AggregatedRelationshipInstance
        @return: the aggregated relationship with filled expectancy and
            description, other fields are empty.
        """ 
        return self._combine(
            combination_elements=combination_elements, 
            ResultClass=AggregatedRelationshipInstance)
        

    def combine_entity_biases(self, entity_biases):
        """Aggregate biases of the given entity S, O, or SO.
        
        @type entitiy_biases: QuerySet, each member having a get_expectancy()
            method
        @param entitiy_biases: the biases to aggregate
        
        @rtype: float
        @return: the expectancy that the entity will be in 
            a predicted_relationship, aggregated from its biases
        """
        return self._combine(
            combination_elements=entity_biases,
            ResultClass=AggregatedBiasInstance)

    def choose_promising_objects(self, dn_subject, min_count):
        """Choose at least min_count objects that are likely to be interesting
        for the dn_subject, using various preference sources, choosing by 
        a heuristic.
        
        Get maximum of min_count objects from each category
         - aggregated object bias 
         - s-o relationships 
         - predicted_relationship + object_similarities
         - predicted_relationship + subject similarities
         - predicted_relationship + subject cluster memberships 
         - predicted_relationship + object cluster memberships 
        
        @type dn_subject: SubjectObject
        @param dn_subject: the subject to choose the objects for
        
        @type min_count: int
        @param min_count: the minimum count that is chosen (if it's available)
        
        @rtype: iterable of SubjectObject
        @return: the promising objects
        """
        
        
        recommender_model = dn_subject.recommender
        
        object_ent_type =  ENTITY_TYPE_SUBJECTOBJECT \
            if recommender_model.are_subjects_objects else \
                ENTITY_TYPE_OBJECT
        
        # aggregated object bias
        #
        
        # use some caching
        if self.top_bias_objects is None:
            
            qs_biases = AggregatedBiasInstance.objects\
                .filter(recommender=recommender_model, 
                    subject_object__entity_type=object_ent_type,
                    expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
                .order_by('-expectancy')[:min_count]
                
            self.top_bias_objects = [b.subject_object for b in qs_biases]
                
        top_bias_objs = self.top_bias_objects
        
        # s-o rules, relationships, explicit rules
        #
        
        top_rel_objs = self._get_promising_objects_rules_relationships(
                            dn_subject=dn_subject,
                            min_count=min_count,
                            recommender_model=recommender_model)
        
            
        # predicted_relationship + object_similarities
        # predicted_relationship + subject similarities
        
        top_sim_objs = self._get_promising_objects_similarities(
                            dn_subject=dn_subject,
                            min_count=min_count,
                            recommender_model=recommender_model)
        
        

        # predicted_relationship + subject cluster memberships 
        # predicted_relationship + object cluster memberships
        
        cluster_objs = self._get_promising_objects_clusters(
                            dn_subject=dn_subject,
                            min_count=min_count,
                            recommender_model=recommender_model)
        
        return list(set(
            top_bias_objs 
            + top_rel_objs 
            + top_sim_objs 
            + cluster_objs
            ))

    def _get_promising_objects_clusters(self, dn_subject, min_count, recommender_model):
        """Get promising objects from predicted_relationship + cluster membership"""

        # the definition of the predicted relationship
        d = PredictedRelationshipDefinition.objects.get(recommender=recommender_model)
        
        # taking similar subjects from clusters
        #
        sim_subj_objs = []

        # go through the subject's memberships
        for cm1 in dn_subject.clustermember_set.order_by('-confidence')[:min_count/self.DIVISOR]:

            # take the most similar subjects
            for cm2 in cm1.cluster.clustermember_set.exclude(id=cm.id).order_by('-confidence')[:min_count/self.DIVISOR]:
                
                # take objects connected with them
                for rel in cm2.member.relationshipinstance_relationships1.filter(definition=d)[:min_count/self.DIVISOR]:
                    
                    sim_subj_objs.append(rel.subject_object2)
        
        # taking similar objects from clusters
        #
        
        qs_memberships = ClusterMember.objects.filter(
            cluster__cluster_set__recommender=recommender_model,
            cluster__clustermember__cluster__cluster_set__recommender=recommender_model,
            cluster__clustermember__member__relationshipinstance_relationships2__definition=d,
            cluster__clustermember__member__relationshipinstance_relationships2__subject_object1=dn_subject)\
            .order_by('-confidence', '-cluster__clustermember__confidence')[:min_count]

        sim_obj_objs = [cm.member for cm in qs_memberships]
        
        return sim_subj_objs + sim_obj_objs
        
    def _get_promising_objects_rules_relationships(self, dn_subject, min_count, recommender_model):
        """Get promising objects from subject-object rules, relationships, explicit rules"""
        
        # get what is available in instances

        # the relationship type we're interested in
        rel_type = RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT \
            if recommender_model.are_subjects_objects else \
                RELATIONSHIP_TYPE_SUBJECT_OBJECT 
        
        # relationship instances by weight, some rules also may be chosen
        qs_rel = RelationshipInstance.objects.filter(
                    definition__recommender=recommender_model,
                    definition__rulerelationshipdefinition__relationship_type=rel_type,
                    subject_object1=dn_subject,
                    definition__rulerelationshipdefinition__is_positive=True)\
                    .order_by('-definition__rulerelationshipdefinition__weight')[:min_count]

        # rule instances by confidence
        qs_rule = RuleInstance.objects.filter(
                    definition__recommender=recommender_model,
                    definition__rulerelationshipdefinition__relationship_type=rel_type,
                    subject_object1=dn_subject,
                    definition__rulerelationshipdefinition__is_positive=True)\
                    .order_by('-confidence')[:min_count]                    

        # explicit feedback                    
        qs_exp_rel = ExplicitRuleInstance.objects.filter(                    
                    definition__recommender=recommender_model,
                    subject_object1=dn_subject,
                    expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
                    .order_by('-expectancy')[:min_count]

        return [rel.subject_object2 for rel in qs_rel] + \
            [rel.subject_object2 for rel in qs_rule] + \
            [rel.subject_object2 for rel in qs_exp_rel]        

        
    def _get_promising_objects_similarities(self, dn_subject, min_count, recommender_model):
        """Get promising objects from predicted_relationship + aggregated similarities"""
        
        # the definition of the predicted relationship
        d = PredictedRelationshipDefinition.objects.get(recommender=recommender_model)
        
        # try finding the similar entities to the ones liked by dn_subject
        # content-based                
        
        # get similarities starting the traverse with the similarity.
        cont_qs_sim1 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model, expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
            .filter(
                # traverse from the other object in similarity (subject_object1) through
                # the relationship instance, its subject (subject_object1) must be so1
                subject_object1__relationshipinstance_relationships2__subject_object1=dn_subject,
                
                # the relationship instance definition must be the predicted relationship def
                subject_object1__relationshipinstance_relationships2__definition=d)\
            .order_by('-expectancy')[:min_count]

        cont_objs_sim1 = [sim.subject_object2 for sim in cont_qs_sim1]

        cont_qs_sim2 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model, expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
            .filter(
                # traverse from the other through relationship to so1
                subject_object2__relationshipinstance_relationships2__subject_object1=dn_subject,
                
                # the definition again must be the predicted
                subject_object2__relationshipinstance_relationships2__definition=d)\
            .order_by('-expectancy')[:min_count]
        
        cont_objs_sim2 = [sim.subject_object1 for sim in cont_qs_sim2]
        
        # try finding the similar entity (user) to entity that liked so2
        # cf
        
        # when subject is in the second position in similarity
        cf_qs_sim1 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model, expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
            .filter(
                # take dn_subject as stable - in the subject_object2 position of the similarity
                subject_object2=dn_subject,
                                
                # the relationship instance definition must be the predicted relationship def
                subject_object1__relationshipinstance_relationships1__definition=d)\
            .order_by('-expectancy')[:min_count/self.DIVISOR]

        # get the object behind the predicted_relationship            
        cf_objs_sim1 = [pref.subject_object2 \
            for sim in cf_qs_sim1 \
            for pref in sim.subject_object1.relationshipinstance_relationships1.filter(definition=d)]

        # when subject is in the first position in similarity                            
        cf_qs_sim2 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model, expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
            .filter(
                # take dn_subject as stable again, now in the subject_object1 position of the similarity
                subject_object1=dn_subject, 
                
                # the definition again must be the predicted
                subject_object2__relationshipinstance_relationships1__definition=d)\
            .order_by('-expectancy')[:min_count/self.DIVISOR]
            
        # get the object behind the predicted_relationship                        
        cf_objs_sim2 = [pref.subject_object2 \
            for sim in cf_qs_sim2 \
            for pref in sim.subject_object2.relationshipinstance_relationships1.filter(definition=d)]
        
        return cont_objs_sim1 + cont_objs_sim2 + cf_objs_sim1 + cf_objs_sim2
        
        
    def combine_pair_prediction_elements(self, combination_elements):
        """Combine all preference sources producing predictions"""
        return self._combine(
            combination_elements=combination_elements,
            ResultClass=RelationshipPredictionInstance)
            
            
            
            
