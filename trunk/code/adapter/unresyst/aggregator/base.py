"""The module defines base class for the aggregator package."""

class BaseAggregator(object):
    """The base (abstract) class for all aggregators. Defines the interface."""    
    
    # Build phase:
    #
    
    @classmethod
    def aggregate(cls, recommender_model):
        """Aggregate the rule and relationship instances.
        
        Aggregates instances of the relationships and rules from 
        the recommender_model to create AggregatedRelationshipInstance
        instances. Instances are saved to db.
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender whose instances should
            be aggregated. 
        """
        pass

    # Update phase:
    # 
    
    @classmethod
    def update(cls, recommender, instance_changes):
        """Apdate the aggregated relationships according to the instance 
        changes.
        
        @rtype: uvidime
        @return: the changes performed on the aggregated relationships. 
        """

