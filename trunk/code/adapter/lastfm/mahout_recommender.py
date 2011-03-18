"""The representation of the Mahout recommender in Unresyst."""

from unresyst.recommender.external_recommender import ExternalRecommender
from recommender import ArtistRecommender, NovelArtistRecommender

class MahoutArtistRecommender(ExternalRecommender, ArtistRecommender):
    """An external artist recommender - both novel and non-novel artists"""
    
    name = "Mahout artist recommender"
    """The name"""
    
class NovelMahoutArtistRecommender(ExternalRecommender, NovelArtistRecommender):
    """External recommender for novel artists only"""
    
    name = "Novel Mahout artist recommender"
    """The name"""
