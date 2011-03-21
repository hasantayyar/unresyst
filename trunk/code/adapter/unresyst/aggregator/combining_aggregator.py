"""The aggregator that uses a combinator to aggregate"""

from base import BaseAggregator
from unresyst.constants import *
from unresyst.models.abstractor import RelationshipInstance, \
    PredictedRelationshipDefinition, Cluster, BiasInstance
from unresyst.models.aggregator import AggregatedRelationshipInstance, \
    AggregatedBiasInstance
from unresyst.combinator.combination_element import RelSimilarityCombinationElement, \
    ClusterSimilarityCombinationElement, BiasCombinationElement  

class CombiningAggregator(BaseAggregator):
    """A class using unresyst.combinator for creating aggregates"""
    
    def aggregate_rules_relationships(self, recommender_model):
        """See the base class for documentation.
        
        Does only similarity aggregation + clusters, the preference aggregation is left out
        for the algorithm.
        """
        # get pairs that have some similarities
        # 
        
        # take all rule/relationship instances, that don't belong 
        # to the predicted_relationship - their id unique pairs
        #
        
        predicted_def = PredictedRelationshipDefinition.objects.get(
                            recommender=recommender_model)

        qs_similarities = RelationshipInstance.objects\
                        .exclude(definition=predicted_def)\
                        .filter(definition__recommender=recommender_model)\
                        .filter(definition__rulerelationshipdefinition__relationship_type__in=[
                            RELATIONSHIP_TYPE_OBJECT_OBJECT,
                            RELATIONSHIP_TYPE_SUBJECT_SUBJECT,
                            RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT])                        
        
        # the unique pairs of entities between which there's some similarity
        qs_id_pairs = qs_similarities\
                        .values_list('subject_object1__id', 'subject_object2__id')\
                        .distinct()
        
        # for all pairs that have some similarity
        for id1, id2 in qs_id_pairs.iterator():
            
            combination_elements = []

            # similarities:
            #
            
            # filter similarities that are for the pair
            # only one direction is needed, because we're taking it from the same source
            qs_pair_similarity = qs_similarities.filter(
                subject_object1__id=id1, 
                subject_object2__id=id2)
            
            # save the entity type - there must be always at least
            # one similarity relationship for the pair, so this is
            # always filled.
            relationship_type = qs_pair_similarity[0].definition.as_leaf_class().relationship_type
            
            # create combining elements from them
            for pair_sim in qs_pair_similarity.iterator():

                el = RelSimilarityCombinationElement(rel_instance=pair_sim)
                combination_elements.append(el)
                    
            # clusters:
            #
            
            # get clusters the two have in common
            qs_common_clusters = Cluster.objects.filter(clustermember__member__id=id1)\
                .filter(clustermember__member__id=id2)
            
            # create the compiling elements from them
            for c in qs_common_clusters.iterator():
                
                el = ClusterSimilarityCombinationElement(
                    cluster_members=[
                        c.clustermember_set.get(member__id=id1),
                        c.clustermember_set.get(member__id=id2)]
                )
                combination_elements.append(el)            
            
            # aggregation and save:
            #
            
            # aggregate the similarity through the combinator
            aggr = self.combinator.combine_pair_similarities(
                combination_elements=combination_elements)
            
            # create and save the aggregated similarity instance
            aggr.subject_object1_id = id1
            aggr.subject_object2_id = id2
            aggr.recommender = recommender_model
            aggr.relationship_type = relationship_type
            aggr.save()

        
    def aggregate_biases(self, recommender_model):
        """See the base class for documentation.
        """
        
        # all available biases
        qs_biases = BiasInstance.objects.filter(definition__recommender=recommender_model)
        
        # get entities that have some biases: subject/object anything
        qs_ids = qs_biases.values_list('subject_object__id', flat=True).distinct()
        
        for ent_id in qs_ids:
            
            # get the biases for the entity
            ent_biases = [BiasCombinationElement(bias_instance=b) for b in qs_biases.filter(subject_object__id=ent_id)]
            
            # throw them to the combinator
            aggr = self.combinator.combine_entity_biases(entity_biases=ent_biases)
            
            # fill the missing fields and save
            aggr.subject_object_id = ent_id
            aggr.recommender = recommender_model
            aggr.save()
            
                            
