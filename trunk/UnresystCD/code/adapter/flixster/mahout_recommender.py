"""The representation of the Mahout recommender in Unresyst."""

from unresyst.recommender.external_recommender import ExternalRecommender
from recommender import MovieRecommender

class MahoutMovieRecommender(ExternalRecommender, MovieRecommender):
    """An external artist recommender - both novel and non-novel artists"""
    
    name = "Mahout movie recommender"
    """The name"""
    
    explicit_rating_rule = MovieRecommender.rules[0]
    """The first one is the explicit one"""
