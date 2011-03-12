"""The base class for all compilators BaseCompilator"""

from unresyst.constants import *

class BaseCompilator(object):
    """The base class for all compilators"""
    
    def __init__(self, depth=DEFAULT_COMPILATOR_DEPTH, breadth=DEFAULT_COMPILATOR_BREADTH):
        """The initializer"""
        
        self.depth = depth
        """The depth until where the comiplates should be done"""
        
        self.breadth = breadth
        """The number of neighbours that will be taken during the compilation"""      

    def compile_all(self, recommender_model):
        """Compile preferences, known relationships + similarities.        
        """
        pass
        
    
    def get_pair_combination_elements(self, dn_subject, dn_object):
        """Find all we know about the relationship of dn_subject and
        dn_subject using:
         - aggregated bias for both
         - s-o relationships (all)
         - predicted_relationship + object_similarities
         - predicted_relationship + subject similarities
         - predicted_relationship + subject cluster memberships (pairs not covered by similarities)
         - predicted_relationship + object cluster memberships (pairs not covered by similarities)
         --------- depth COMPILATOR_DEPTH_ONE_UNSURE
         
        @type dn_subject, dn_object: SubjectObject 
        @param dn_subject, dn_object: the pair to get combination elements for
         
        @rtype: iterable of BaseCombinationElement
        @return: the list of all we know about the pair
        """
        
        
