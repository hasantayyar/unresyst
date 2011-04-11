"""The representation of the Mahout recommender in Unresyst."""

from unresyst.recommender.external_recommender import ExternalRecommender
from recommender import OrderTourRecommender

from models import *

class MahoutOrderTourRecommender(ExternalRecommender, OrderTourRecommender):
    """An external order tour recommender"""
    
    name = "Mahout order tour recommender"
    """The name"""
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = Tour.objects
    """The objects that will be recommended.""" 
