"""The base class for all compilators BaseCompilator"""

from unresyst.constants import *
from unresyst.combinator.combination_element import BiasAggregateCombinationElement, \
    SubjectObjectRelCombinationElement
from unresyst.models.aggregator import AggregatedBiasInstance
from unresyst.models.abstractor import PredictedRelationshipDefinition, RelationshipInstance


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
        recommender_model = dn_subject.recommender
        els = []
        
        #  aggregated bias for both
        qs_bias = AggregatedBiasInstance.objects.filter(
            subject_object__id__in=[dn_subject.id, dn_object.id])
        
        for bias in qs_bias:
            els.append(BiasAggregateCombinationElement(bias_aggregate=bias))
        
        # s-o relationships (all)
        #
        
        predicted_def = PredictedRelationshipDefinition.objects.get(
                            recommender=recommender_model)
        qs_rels = RelationshipInstance.objects\
                        .exclude(definition=predicted_def)\
                        .filter(definition__recommender=recommender_model)\
                        .filter(subject_object1=dn_subject, subject_object2=dn_object)
                        
        for rel in qs_rels:
            els.append(SubjectObjectRelCombinationElement(rel_instance=rel))
        
                                               
        # predicted_relationship + object_similarities
        #
        
        
        
        # predicted_relationship + subject similarities
        # predicted_relationship + subject cluster memberships (pairs not covered by similarities)
        # predicted_relationship + object cluster memberships (pairs not covered by similarities)
        
        return els
        
        from unresyst.models.abstractor import BiasInstance
        b = BiasInstance.objects.all()[0]
        
        return [BiasCombinationElement(b)]
        
        
