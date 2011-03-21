"""The representation of the Mahout recommender in Unresyst."""

from unresyst.recommender.external_recommender import ExternalRecommender
from recommender import OrderTourRecommender

class MahoutOrderTourRecommender(ExternalRecommender, OrderTourRecommender):
    """An external order tour recommender"""
    
    name = "Mahout order tour recommender"
    """The name"""
    

