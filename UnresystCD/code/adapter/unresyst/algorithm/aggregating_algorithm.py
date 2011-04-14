"""The aggregating algorithm class"""

from base import BaseAlgorithm

class AggregatingAlgorithm(BaseAlgorithm):
    """The algorithm that aggregates the similarity relationships and biases,
    uses the compiling algorithm as its inner_algorithm.
    """
    
    def __init__(self, inner_algorithm, aggregator):
        """The initializer"""
                
        super(AggregatingAlgorithm, self).__init__(inner_algorithm=inner_algorithm)
        
        self.aggregator=aggregator
        """The aggregator that will be used for aggregating the relationships
        and biases"""
        
    def build(self, recommender_model):
        """See the base class for documentation.
        
        Aggregates and calls the inner algorithm build
        """
        
        # aggregate the relationships and rules
        self.aggregator.aggregate_rules_relationships(
            recommender_model=recommender_model)        
        
        # aggregate the biases
        self.aggregator.aggregate_biases(recommender_model=recommender_model)
        
        print "Rules, relationships and biases aggregated. Building the inner algorithm..."
        
        super(AggregatingAlgorithm, self).build(recommender_model=recommender_model)
