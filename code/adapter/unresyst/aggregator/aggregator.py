"""The main class of the aggregator package - Aggregator"""

from base import BaseAggregator
from unresyst.models.abstractor import RelationshipInstance
from unresyst.models.aggregator import AggregatedRelationshipInstance
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
        
        # vzit vsechny modely v relationshipInstance - podle politiky na zahrnovani predicted relationship
        # ji tam bud zahrnout nebo ne. 
        # 
        # projet vsechny pary, vytahnout z toho ^ instance pro par. kdyz nejaky existuje tak
        # na vsech instancich zavolat .get_linear_expectancy - ta to bude nasobit - na modelu
        # udelat instanci toho myho vtipu
                        
            
            
            
        
