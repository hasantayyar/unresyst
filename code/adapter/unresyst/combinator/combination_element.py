"""The elements that are given to combinators to combine them. 
Instancies of the classes represent knowledge that we have about a pair
to count similarity/preference."""

class BaseCombinationElement(object):
    """The base for all elements that are being combined in combinator"""
    
    def get_positiveness(self):
        """Is the element positive/negative to the combination?"""
        pass
        
    def get_expectancy(self):
        """The expectancy of the element"""
        pass
        
    def get_description(self):
        """The description of the element"""        
        pass
                                        
    
class SimilarityCombinationElement(BaseCombinationElement):
    """The element of a similarity combination"""
    pass
    
class RelSimilarityCombinationElement(SimilarityCombinationElement):
    """The similarity coming out of a rule/relationship"""
    
    def __init__(self, rel_instance):
        """The initializer"""
        
        self.rel_instance = rel_instance
        """The rule/relationship instance the similarity is obtained from"""
        
    def get_positiveness(self):
        return self.rel_instance.definition.as_leaf_class().is_positive

    def get_expectancy(self):
        return self.rel_instance.get_expectancy()        
        
    def get_description(self):
        return self.rel_instance.description        


class ClusterSimilarityCombinationElement(SimilarityCombinationElement):
    """The similarity coming out of a common cluster memenbership"""

    def __init__(self, cluster_members):
        """The initializer"""
        
        self.cluster_members = cluster_members
        """The pair of cluster members that caused the similarity"""
    
    def get_positiveness(self):
        """Cluster membership is always positive"""
        return True
    
    def get_expectancy(self):
        """Return the product of the reasoning members"""
        member1, member2 = self.cluster_members
        return member1.get_expectancy() * member2.get_expectancy()
    
    def get_description(self):
        """Return the concatenaged member descriptions"""
        return " ".join(cm.description for cm in self.cluster_members)
        
        
