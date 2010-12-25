"""The main class of the aggregator package - Aggregator"""

from base import BaseAggregator
from unresyst.models.abstractor import RelationshipInstance, \
    PredictedRelationshipDefinition
from unresyst.models.aggregator import AggregatedRelationshipInstance
from unresyst.models.common import SubjectObject
from unresyst.exceptions import InvalidParameterError

class LinearAggregator(BaseAggregator):
    """The class aggregating rule/relationship instances to one for each pair
    of entities. 
    
    It ignores the predicted_relationship instances.
    """

    @classmethod
    def aggregate(cls, recommender_model):
        """For documentation see the base class.
        
        Linearly combines the rule and relationship instances.
        """
        
        # if there's something in the database for the recommender
        # throw an error
        if  AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model).exists():
            
            raise InvalidParameterError(
                message="There're unexpected aggregated instances for the recommender.", 
                parameter_name="recommender_model", 
                parameter_value=recommender_model)

        # aggregate it
        # 
        
        # take all rule/relationship instances, that don't belong 
        # to the predicted_relationship
        predicted_def = PredictedRelationshipDefinition.objects.get(
                            recommender=recommender_model)
        instance_qs = RelationshipInstance.objects\
                        .exclude(definition=predicted_def)\
                        .filter(definition__recommender=recommender_model)
                                            
        
        # for all pairs of subjectobjects no matter if they're subjects,
        # objects or both, take all pairs once
        for ent1, ent2 in SubjectObject.unique_pairs(
                             recommender=recommender_model,
                             entity_type=None):
            
            # get relationships between ent1 and ent2
            pairs_qs = RelationshipInstance.filter_relationships(
                        object1=ent1,
                        object2=ent2,
                        queryset=instance_qs)

            if not pairs_qs:
                continue
            
            # if there're some relationship instances, create an aggregated
            # instance and save it
            
            # description are joined descriptions of the relationships
            desc = ' '.join([pair.description for pair in pairs_qs])
            
            # expectancy is an average expectancy
            exp = sum([pair.get_linear_expectancy() for pair in pairs_qs])\
                    / pairs_qs.count()
            
            aggr_inst = AggregatedRelationshipInstance(
                            subject_object1=ent1,
                            subject_object2=ent2, 
                            description=desc,
                            expectancy=exp,
                            recommender=recommender_model)
            
            aggr_inst.save()
            
            
        
