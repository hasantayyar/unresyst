"""The elements that are given to combinators to combine them. 
Instancies of the classes represent knowledge that we have about a pair
to count similarity/preference."""

from unresyst.constants import *

def _get_expectancy_positiveness(expectancy):
    return expectancy > UNCERTAIN_PREDICTION_VALUE

class BaseCombinationElement(object):
    """The base for all elements that are being combined in combinator"""
    
    def __init__(self):
        """Initialize the members"""
        self._positiveness = None
        self._expectancy = None
        self._description = None
    
    def get_positiveness(self):
        """Is the element positive/negative to the combination?"""
        if self._positiveness is None:
            self._positiveness = self._get_positiveness()
        
        return self._positiveness
        
    def get_expectancy(self):
        """The expectancy of the element"""
        
        if self._expectancy is None:
            self._expectancy = self._get_expectancy()
            
        return self._expectancy
        
    def get_description(self):
        """The description of the element"""        
        
        if self._description is None:
            self._description = self._get_description()
        
        return self._description

    def _get_positiveness(self):
        pass

    def _get_expectancy(self):
        pass
        
    def _get_description(self):
        pass
        
    def __repr__(self):
        return "<%f, %s, %s>" % (self.get_expectancy(), self.get_positiveness(), self.get_description())        

class SubjectObjectRelCombinationElement(BaseCombinationElement):
    """The relationship between a subject and an object meaning the preference
    in means of the predicted_relationship.    
    """
    
    def __init__(self, rel_instance):
        """The initializer"""
        
        super(SubjectObjectRelCombinationElement, self).__init__()
        
        self.rel_instance = rel_instance

    def _get_positiveness(self):
        return self.rel_instance.definition.as_leaf_class().is_positive

    def _get_expectancy(self):
        return self.rel_instance.get_expectancy()        
        
    def _get_description(self):
        return self.rel_instance.description   
                
    
class SimilarityCombinationElement(BaseCombinationElement):
    """The element of a similarity combination"""
    pass
    
class RelSimilarityCombinationElement(SimilarityCombinationElement):
    """The similarity coming out of a rule/relationship
    
    For Aggregator.
    """
    
    def __init__(self, rel_instance):
        """The initializer"""
        
        super(RelSimilarityCombinationElement, self).__init__()
        
        self.rel_instance = rel_instance
        """The rule/relationship instance the similarity is obtained from
        @type rel_instance: RelationshipInstance
        """
        
    def _get_positiveness(self):
        return self.rel_instance.definition.as_leaf_class().is_positive

    def _get_expectancy(self):
        return self.rel_instance.get_expectancy()        
        
    def _get_description(self):
        return self.rel_instance.description        


class ClusterSimilarityCombinationElement(SimilarityCombinationElement):
    """The similarity coming out of a common cluster memenbership"""

    def __init__(self, cluster_members):
        """The initializer"""
        
        super(ClusterSimilarityCombinationElement, self).__init__()
        
        self.cluster_members = cluster_members
        """The pair of cluster members that caused the similarity
        @type cluster_members: pair ClusterMember, ClusterMember
        """
    
    def _get_positiveness(self):
        """Cluster membership is always positive"""
        return True
    
    def _get_expectancy(self):
        """Return the product of the reasoning members"""
        member1, member2 = self.cluster_members
        return member1.get_expectancy() * member2.get_expectancy()
    
    def _get_description(self):
        """Return the concatenaged member descriptions"""
        return " ".join(cm.description for cm in self.cluster_members)
        
class BiasCombinationElement(BaseCombinationElement):
    """The biase of a subject/object coming to the combination
    For aggregator
    """
    
    def __init__(self, bias_instance):
        """The initializer"""
        
        super(BiasCombinationElement, self).__init__()
        
        self.bias_instance = bias_instance
        """Bias instance. 
        @type bias_instance: BiasInstance
        """    


    def _get_positiveness(self):
        return self.bias_instance.definition.is_positive
    
    def _get_expectancy(self):
        return self.bias_instance.get_expectancy()

    def _get_description(self):
        return self.bias_instance.description

class BiasAggregateCombinationElement(BaseCombinationElement):
    """The aggregated bias of a subject/object.    
    For compilator.
    """
    
    def __init__(self, bias_aggregate):
        """The initializer"""
        
        super(BiasAggregateCombinationElement, self).__init__()
        
        self.bias_aggregate = bias_aggregate
        """The aggregated bias.
        @type bias_aggregate: AggregatedBiasInstance
        """
        
    def _get_positiveness(self):   
        exp = self.get_expectancy()
        return _get_expectancy_positiveness(exp)
        
    def _get_expectancy(self):
        return self.bias_aggregate.expectancy
        
    def _get_description(self):
        return self.bias_aggregate.description


        
