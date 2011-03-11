"""Base classes for the combinator layer:
 - BaseCombinator
"""

class BaseCombinator(object):
    """The empty base class defining the interface of all combinators."""
    
    def aggregate_pair_similarities(self, pair_similarities, 
            cluster_member_expectancies):
        """Aggregate similarities of the given pair S-S, O-O, or SO-SO. 
        
        @type pair_similarities: QuerySet, each member having a get_expectancy() 
            method
        @param pair_similarities: the similarity objects that should 
            be aggregated
        
        @type cluster_member_expectancies: pairs float, float
        @param cluster_member_expectancies: for each cluster the entities 
            of the pair belong to and should be counted, the parameter 
            contains a pair:
            (expectancy of the first belonging to cluster, the expectancy of the second)
            
        @rtype: float
        @return: the expectancy that the pair is similar, aggregated from the
            similarities and cluster members
        """ 
        pass
        

    def aggregate_entity_biases(self, entitiy_biases):
        """Aggregate biases of the given entity S, O, or SO.
        
        @type entitiy_biases: QuerySet, each member having a get_expectancy()
            method
        @param entitiy_biases: the biases to aggregate
        
        @rtype: float
        @return: the expectancy that the entity will be in 
            a predicted_relationship, aggregated from its biases
        """
        pass
        
    def combine_sources(self, x, y, z):
        """Combine all preference sources producing predictions"""
        pass
