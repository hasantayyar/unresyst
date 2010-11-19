"""The module defines base class for the aggregator package."""

class BaseAggregator(object):
    """The base (abstract) class for all aggregators. Defines the interface."""    
    
    # Build phase:
    #
    
    @classmethod
    def aggregate(cls,recommender):
        """Aggregate the rule and relationship instances."""
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

