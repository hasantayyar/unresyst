"""The representation of the Mahout recommender in Unresyst."""

from unresyst.recommender.external_recommender import ExternalRecommender
from recommender import ArtistRecommender

class MahoutArtistRecommender(ExternalRecommender, ArtistRecommender):
    """An external artist recommender"""
    
    name = "Mahout artist recommender"
    """The name"""
