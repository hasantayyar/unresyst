"""The aggregator that uses a combinator to aggregate"""

from base import BaseAggregator
from unresyst.models.abstractor import RelationshipInstance, \
    PredictedRelationshipDefinition
from unresyst.models.aggregator import AggregatedRelationshipInstance, \
    AggregatedBiasInstance

class CombiningAggregator(BaseAggregator):
    """A class using unresyst.combinator for creating aggregates"""
    
    def aggregate_rules_relationships(self, recommender_model):
        """See the base class for documentation.
        
        Does only similarity aggregation, the preference aggregation is left out
        for the algorithm.
        """
        # get pairs that have some similarities
        # 
        
        # take all rule/relationship instances, that don't belong 
        # to the predicted_relationship - their id unique pairs
        predicted_def = PredictedRelationshipDefinition.objects.get(
                            recommender=recommender_model)

        #.exclude(definition__rel)\ ???                            
        qs_similarities = RelationshipInstance.objects\
                        .exclude(definition=predicted_def)\
                        .filter(definition__recommender=recommender_model)\
                        .filter(definition__rulerelationshipdefinition__relationship_type__in=[
                            RELATIONSHIP_TYPE_OBJECT_OBJECT,
                            RELATIONSHIP_TYPE_SUBJECT_SUBJECT,
                            RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT])                        

        # TODO add there pairs that have a cluster in common
        qs_id_pairs = qs_similarities\
                        .values_list('subject_object1__id', 'subject_object2__id')\
                        .distinct()
        
        # for all pairs that have some similarity
        for id1, id2 in qs_id_pairs.iterator():
            
            # filter similarities that are for the pair
            qs_pair_similarity = qs_similarities.filter(
                subject_object1__id=id1, 
                subject_object2__id=id2)
            
            # get cluster members the two have in common
            
            # extract the pairs of expectancies
            
            # aggregate the similarity through the combinator
            aggr_expectancy = self.combinator.aggregate_pair_similarities(
                pair_similarities, 
                cluster_member_expectancies)
            
            # create and save the aggregated similarity instance

        
    def aggregate_biases(self, recommender_model):
        """See the base class for documentation.
        """
        pass
