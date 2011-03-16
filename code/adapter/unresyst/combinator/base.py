"""Base classes for the combinator layer:
 - BaseCombinator
"""
from unresyst.exceptions import CombinatorError
from unresyst.models.abstractor import RelationshipInstance, RuleInstance, \
    ExplicitRuleInstance, PredictedRelationshipDefinition, ClusterMember
from unresyst.models.aggregator import AggregatedRelationshipInstance, AggregatedBiasInstance
from unresyst.models.algorithm import RelationshipPredictionInstance
from unresyst.constants import *

class BaseCombinator(object):
    """The base class defining the interface of all combinators.
    interface methods:
     - combine_pair_similarities
     - combine_entity_biases
     - combine_pair_prediction_elements
     - choose_promising_objects
        
    methods to be overriden:
     - _combine     
     
    helper methods for subclasses:
     - _concat_descriptions        
    """
    
    DIVISOR = 3
    """A constant for dividing the relationship members that would otherwise be 
    too numerous"""
    
    def __init__(self):
        """The initializer"""
        
        self.top_bias_objects = None

    def _checked_combine(self, combination_elements, ResultClass):
        """Check if something was given and call the overriden _combine method
        """
        if not combination_elements:
            raise CombinatorError("No combination_elements given")
        return self._combine(combination_elements, ResultClass)
                    
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

    @staticmethod
    def _concat_descriptions(element_list):
        """Concat descriptions of the elements in the element_list.
        
        @type element_list: a list of BaseCombinationElement
        @param element_list: a list of elements in order that they should
            appear
            
        @rtype: str
        @return: the string concatenation of the element descriptions
        """
        list_len = len(element_list)
        
        assert list_len > 0
        
        if list_len == 1:
            return element_list[0].get_description()
        
        return ' '.join(["%s: %s" % ((REASON_STR % i), e.get_description()) \
            for e, i in zip(element_list, range(1, list_len + 1))])

            

    def combine_pair_similarities(self, combination_elements):
        """Aggregate similarities of the given pair S-S, O-O, or SO-SO. 
        
        @type combination_elements: a list of BaseCombinationElement
        @param combination_elements: the elements that should be combined        
            
        @rtype: AggregatedRelationshipInstance
        @return: the aggregated relationship with filled expectancy and
            description, other fields are empty.
        """ 
        return self._checked_combine(
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
        return self._checked_combine(
            combination_elements=entity_biases,
            ResultClass=AggregatedBiasInstance)


    def combine_pair_prediction_elements(self, combination_elements):
        """Combine all preference sources producing predictions"""
        return self._checked_combine(
            combination_elements=combination_elements,
            ResultClass=RelationshipPredictionInstance)

            
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
                .order_by('-expectancy')
                
            self.top_bias_objects = [(b.subject_object, b.expectancy) for b in qs_biases[:min_count]]
                
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

        # concat all the list and sort by expectancy
        ret_list = top_bias_objs + top_rel_objs + top_sim_objs + cluster_objs
        ret_list.sort(key=lambda pair: pair[1], reverse=True)                
        
        # remove the duplicates and take only some of the first
        return list(set([obj for obj, x in ret_list[:2*min_count]]))

    def _get_promising_objects_clusters(self, dn_subject, min_count, recommender_model):
        """Get promising objects from predicted_relationship + cluster membership

        @return: list of pairs (object, expectancy)
        """

        # the definition of the predicted relationship
        d = PredictedRelationshipDefinition.objects.get(recommender=recommender_model)
        
        # taking similar subjects from clusters
        #
        sim_subj_objs = []

        # go through the subject's memberships
        for cm1 in dn_subject.clustermember_set.order_by('-confidence')[:min_count/(2*self.DIVISOR)]:

            # take the most similar subjects
            for cm2 in cm1.cluster.clustermember_set.exclude(id=cm1.id).order_by('-confidence')[:min_count/(2*self.DIVISOR)]:
                
                # take objects connected with them
                for rel in cm2.member.relationshipinstance_relationships1.filter(definition=d)[:min_count/self.DIVISOR]:
                    
                    # use a approximation for overall expectancy
                    sim_subj_objs.append((rel.subject_object2, 
                        (cm1.confidence * cm2.confidence)/2 + UNCERTAIN_PREDICTION_VALUE))
        
        # taking similar objects from clusters
        #
        
        qs_memberships = ClusterMember.objects.filter(
            cluster__cluster_set__recommender=recommender_model,
            cluster__clustermember__member__relationshipinstance_relationships2__definition=d,
            cluster__clustermember__member__relationshipinstance_relationships2__subject_object1=dn_subject)\
            .order_by('-confidence', '-cluster__clustermember__confidence')

        sim_obj_objs = [(cm.member, cm.confidence/2 + UNCERTAIN_PREDICTION_VALUE) \
            for cm in qs_memberships[:min_count]]
        
        return sim_subj_objs + sim_obj_objs
        
    def _get_promising_objects_rules_relationships(self, dn_subject, min_count, recommender_model):
        """Get promising objects from subject-object rules, relationships,
        explicit rules
        
        @return: list of pairs (object, expectancy)        
        """
        
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
                    .distinct()\
                    .order_by('-definition__rulerelationshipdefinition__weight')

        # rule instances by confidence
        qs_rule = RuleInstance.objects.filter(
                    definition__recommender=recommender_model,
                    definition__rulerelationshipdefinition__relationship_type=rel_type,
                    subject_object1=dn_subject,
                    definition__rulerelationshipdefinition__is_positive=True)\
                    .distinct()\
                    .order_by('-confidence')                   

        # explicit feedback                    
        qs_exp_rel = ExplicitRuleInstance.objects.filter(                    
                    definition__recommender=recommender_model,
                    subject_object1=dn_subject,
                    expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
                    .distinct()\
                    .order_by('-expectancy')

        return [(rel.subject_object2, rel.get_expectancy()) for rel in qs_rel[:min_count]] + \
            [(rel.subject_object2, rel.get_expectancy()) for rel in qs_rule[:min_count]] + \
            [(rel.subject_object2, rel.expectancy) for rel in qs_exp_rel[:min_count]]        

        
    def _get_promising_objects_similarities(self, dn_subject, min_count, recommender_model):
        """Get promising objects from 
        predicted_relationship + aggregated similarities
        
        @return: list of pairs (object, expectancy)
        """
        
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
            .distinct()\
            .order_by('-expectancy')

        cont_objs_sim1 = [(sim.subject_object2, sim.expectancy) for sim in cont_qs_sim1[:min_count]]

        cont_qs_sim2 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model, expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
            .filter(
                # traverse from the other through relationship to so1
                subject_object2__relationshipinstance_relationships2__subject_object1=dn_subject,
                
                # the definition again must be the predicted
                subject_object2__relationshipinstance_relationships2__definition=d)\
            .distinct()\
            .order_by('-expectancy')
        
        cont_objs_sim2 = [(sim.subject_object1, sim.expectancy) for sim in cont_qs_sim2[:min_count]]
        
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
            .distinct()\
            .order_by('-expectancy')

        # get the object behind the predicted_relationship            
        cf_objs_sim1 = [(pref.subject_object2, sim.expectancy) \
            for sim in cf_qs_sim1[:min_count/self.DIVISOR] \
            for pref in sim.subject_object1.relationshipinstance_relationships1.filter(definition=d)[:min_count/self.DIVISOR]]

        # when subject is in the first position in similarity                            
        cf_qs_sim2 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model, expectancy__gt=UNCERTAIN_PREDICTION_VALUE)\
            .filter(
                # take dn_subject as stable again, now in the subject_object1 position of the similarity
                subject_object1=dn_subject, 
                
                # the definition again must be the predicted
                subject_object2__relationshipinstance_relationships1__definition=d)\
            .distinct()\
            .order_by('-expectancy')
            
        # get the object behind the predicted_relationship                        
        cf_objs_sim2 = [(pref.subject_object2, sim.expectancy) \
            for sim in cf_qs_sim2[:min_count/self.DIVISOR] \
            for pref in sim.subject_object2.relationshipinstance_relationships1.filter(definition=d)[:min_count/self.DIVISOR]]
        
        return cont_objs_sim1 + cont_objs_sim2 + cf_objs_sim1 + cf_objs_sim2
        
        

            
            
            
            
