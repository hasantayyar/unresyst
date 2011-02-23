"""The evaluators for the last.fm recommenders"""

from unresyst.recommender.evaluation import BaseEvaluator
from models import ArtistRecommenderEvaluationPair
from unresyst.recommender.metrics import rmse

class ArtistRecommenderEvaluator(BaseEvaluator):
    """The evaluator of the artist recommender"""
    
    EvaluationPairModel = ArtistRecommenderEvaluationPair
    """The model - pairs"""
    
    prediction_metric = rmse
    """The metric"""
    
    
