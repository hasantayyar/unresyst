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
    
    A better aggregator could add the positive and subtract the negative 
    expectances somehow.
    """

    @classmethod
    def aggregate(cls, recommender_model):
        """For documentation see the base class.
        
        Linearly combines the rule and relationship instances.
        
        The descriptions of the aggregates are made by joining the descriptions
        of the aggregated instances. The descriptions are ordered by the expectancy
        of their owners, the highest expectancy comes first.
        """
        
        # if there's something in the database for the recommender
        # throw an error
        if  AggregatedRelationshipInstance.objects\
            .filter(recommender=recommender_model).exists():
            
            raise InvalidParameterError(
                message="There're unexpected aggregated instances for the recommender.", 
                recommender=cls,
                parameter_name="recommender_model", 
                parameter_value=recommender_model)

        # aggregate it
        # 
        
        # take all rule/relationship instances, that don't belong 
        # to the predicted_relationship
        # order them by the first and the second
        predicted_def = PredictedRelationshipDefinition.objects.get(
                            recommender=recommender_model)
        instance_qs = RelationshipInstance.objects\
                        .exclude(definition=predicted_def)\
                        .filter(definition__recommender=recommender_model)\
                        .order_by('subject_object1__id', 'subject_object2__id')
        
        # if there's nothing to aggregate, schluss
        if not instance_qs:
            return
            
        first_inst = instance_qs[0]
        
        # continuously built aggregated instance
        # initialize it wit the first instance
        cont_inst = AggregatedRelationshipInstance(
                subject_object1=first_inst.subject_object1,
                subject_object2=first_inst.subject_object2, 
                relationship_type=first_inst.definition.as_leaf_class().relationship_type,
                recommender=recommender_model)

        exp = first_inst.get_expectancy()
        exp_sum = exp
        count = 1    
        # a list of pairs (expectancy, description)            
        desc_list =  [(exp, first_inst.description), ]
                    
        # go through the rel instances                        
        for instance in instance_qs.exclude(pk=first_inst.pk).iterator():            
            
            # if the pair has chnged from the last pair, save what we've got and 
            # start anew
            if cont_inst.subject_object1 <> instance.subject_object1 \
                or cont_inst.subject_object2 <> instance.subject_object2:
                
                # count the average expectancy
                cont_inst.expectancy = float(exp_sum) / count
                
                # sort the description list by expectancy and join it
                desc_list.sort(key=lambda pair: pair[0], reverse=True)                
                cont_inst.description = ' '.join([desc for x, desc in desc_list])

                # save the current instance
                cont_inst.save()
                
                # start a new continuously aggregated instance
                cont_inst = AggregatedRelationshipInstance(
                    subject_object1=instance.subject_object1,
                    subject_object2=instance.subject_object2, 
                    relationship_type=instance.definition.as_leaf_class().relationship_type,
                    recommender=recommender_model)
                
                exp = instance.get_expectancy()
                exp_sum = exp
                count = 1                    
                
                # a list of pairs (expectancy, description)            
                desc_list =  [(exp, instance.description), ]
            
            # otherwise aggregate                    
            else:         
                exp = instance.get_expectancy()                         
                exp_sum += exp
                count += 1
                
                desc_list.append((exp, instance.description))
                
                
        # count and save the last we have
        # 
                                                        
        # count the average expectancy
        cont_inst.expectancy = float(exp_sum) / count
        
        # sort the description list by expectancy and join it
        desc_list.sort(key=lambda pair: pair[0], reverse=True)                
        cont_inst.description = ' '.join([desc for x, desc in desc_list])

        # save the last instance
        cont_inst.save()
        
 
