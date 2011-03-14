"""The base class for all compilators BaseCompilator"""
from django.db.models import Q

from unresyst.constants import *
from unresyst.combinator.combination_element import BiasAggregateCombinationElement, \
    SubjectObjectRelCombinationElement, PredictedPlusObjectSimilarityCombinationElement, \
    PredictedPlusSubjectSimilarityCombinationElement, PredictedPlusObjectClusterMemberCombinationElement, \
    PredictedPlusSubjectClusterMemberCombinationElement, ClusterSimilarityCombinationElement
from unresyst.models.aggregator import AggregatedBiasInstance, AggregatedRelationshipInstance
from unresyst.models.abstractor import PredictedRelationshipDefinition, RelationshipInstance, \
    ClusterMember


class BaseCompilator(object):
    """The base class for all compilators"""
    
    def __init__(self, combinator=None, depth=DEFAULT_COMPILATOR_DEPTH, breadth=DEFAULT_COMPILATOR_BREADTH):
        """The initializer"""

        self.combinator = combinator
        """The combinator that will be used in compiling (e.g. the combination of cluster members
        to get similarity. If None, the get first strategy is used.
        """        
        
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
        other_objs = []
        other_subjs = []        
        
        predicted_def = PredictedRelationshipDefinition.objects.get(
                            recommender=recommender_model)
        #  aggregated bias for both
        qs_bias = AggregatedBiasInstance.objects.filter(
            subject_object__id__in=[dn_subject.id, dn_object.id])
        
        for bias in qs_bias:
            els.append(BiasAggregateCombinationElement(bias_aggregate=bias))

        # s-o relationships (all)
        #
        
               
        qs_rels = RelationshipInstance.objects\
                        .exclude(definition=predicted_def)\
                        .filter(definition__recommender=recommender_model)\
                        .filter(subject_object1=dn_subject, subject_object2=dn_object)
                        
        for rel in qs_rels:
            els.append(SubjectObjectRelCombinationElement(rel_instance=rel))
        
        # predicted_relationship + object_similarities
        #

        # get similarities starting the traverse with the similarity.
        qs_sim1 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model)\
            .filter(
                Q(
                    # take dn_object as stable - in the subject_object2 position of the similarity
                    subject_object2=dn_object,
                    
                    # traverse from the other object in similarity (subject_object1) through
                    # the relationship instance, its subject (subject_object1) must be dn_subject
                    subject_object1__relationshipinstance_relationships2__subject_object1=dn_subject,
                    
                    # the relationship instance definition must be the predicted relationship def
                    subject_object1__relationshipinstance_relationships2__definition=predicted_def) | \
                Q(  
                    # take dn_object as stable again, now in the subject_object1 position of the similarity
                    subject_object1=dn_object, 
                    
                    # traverse from the other through relationship to dn_subject
                    subject_object2__relationshipinstance_relationships2__subject_object1=dn_subject,
                    
                    # the definition again must be the predicted
                    subject_object2__relationshipinstance_relationships2__definition=predicted_def)).distinct()
        

        
        # create combination elements
        for sim_rel in qs_sim1:
            
            # get the object that is similar to dn_object
            other_obj = sim_rel.get_related(dn_object)
            
            other_objs.append(other_obj)
            
            # get the predicted relationship to the other object
            predicted_rel = RelationshipInstance.objects.get(
                definition=predicted_def, 
                subject_object1=dn_subject,
                subject_object2=other_obj)
        
            els.append(PredictedPlusObjectSimilarityCombinationElement(
                predicted_rel=predicted_rel,
                similarity_aggregate=sim_rel))
            

        
        # predicted_relationship + subject similarities
        #
        qs_sim2 = AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model)\
            .filter(
                Q(
                    # take dn_subject as stable - in the subject_object2 position of the similarity
                    subject_object2=dn_subject,
                    
                    # traverse from the other object in similarity (subject_object1) through
                    # the relationship instance, its object (subject_object2) must be dn_object
                    subject_object1__relationshipinstance_relationships1__subject_object2=dn_object,
                    
                    # the relationship instance definition must be the predicted relationship def
                    subject_object1__relationshipinstance_relationships1__definition=predicted_def) | \
                Q(  
                    # take dn_subject as stable again, now in the subject_object1 position of the similarity
                    subject_object1=dn_subject, 
                    
                    # traverse from the other through relationship to dn_object
                    subject_object2__relationshipinstance_relationships1__subject_object2=dn_object,
                    
                    # the definition again must be the predicted
                    subject_object2__relationshipinstance_relationships1__definition=predicted_def)).distinct()
        
        # create combination elements
        for sim_rel in qs_sim2:
            
            # get the object that is similar to dn_object
            other_subj = sim_rel.get_related(dn_subject)

            other_subjs.append(other_subj)
           
            
            # get the predicted relationship to the other subject
            predicted_rel = RelationshipInstance.objects.get(
                definition=predicted_def, 
                subject_object1=other_subj,
                subject_object2=dn_object)
        
            els.append(PredictedPlusSubjectSimilarityCombinationElement(
                predicted_rel=predicted_rel,
                similarity_aggregate=sim_rel))

                           
        
        # predicted_relationship + object cluster memberships (pairs not covered by similarities)        
        # 
        
        # take the second membership from the object (first on the path from subject)
        # exclude the trivial cases
        qs_memberships_o = ClusterMember.objects.filter(
            cluster__cluster_set__recommender=recommender_model,
            cluster__clustermember__member=dn_object,
            member__relationshipinstance_relationships2__definition=predicted_def,
            member__relationshipinstance_relationships2__subject_object1=dn_subject)\
            .exclude(member=dn_object)\
            .distinct()
        
        # create the combination elements       
        for cm in qs_memberships_o:
        
            # dont include the ones that are already there because of the similarity
            if cm.member in other_objs:
                continue
            
            # get the predicted relationship to the subject
            predicted_rel = RelationshipInstance.objects.get(
                definition=predicted_def, 
                subject_object1=dn_subject,
                subject_object2=cm.member)
                
            # get the other membership
            second_membership = ClusterMember.objects.get(
                cluster=cm.cluster,
                member=dn_object)
            
            # create the combination element out of the memberships    
            ce = ClusterSimilarityCombinationElement(
                cluster_members=(cm, second_membership))                
                
            els.append(PredictedPlusObjectClusterMemberCombinationElement(
                predicted_rel=predicted_rel,
                cluster_combination_element=ce))                                
          
          
        # predicted_relationship + subject cluster memberships (pairs not covered by similarities)    
        # 
        
        # take the second membership from the subject
        # exclude the trivial cases
        qs_memberships_s = ClusterMember.objects.filter(
            cluster__cluster_set__recommender=recommender_model,
            cluster__clustermember__member=dn_subject,
            member__relationshipinstance_relationships1__definition=predicted_def,
            member__relationshipinstance_relationships1__subject_object2=dn_object)\
            .exclude(member=dn_subject)\
            .distinct()
        
        # create the combination elements       
        for cm in qs_memberships_s:
        
            # dont include the ones that are already there because of the similarity
            if cm.member in other_subjs:
                continue
            
            # get the predicted relationship to the object
            predicted_rel = RelationshipInstance.objects.get(
                definition=predicted_def, 
                subject_object1=cm.member,
                subject_object2=dn_object)
                
            # get the other membership
            first_membership = ClusterMember.objects.get(
                cluster=cm.cluster,
                member=dn_subject)
            
            # create the combination element out of the memberships    
            ce = ClusterSimilarityCombinationElement(
                cluster_members=(first_membership, cm))                
            
            # append the element to the result    
            els.append(PredictedPlusSubjectClusterMemberCombinationElement(
                predicted_rel=predicted_rel,
                cluster_combination_element=ce))             
        
        return els
        
        
        
