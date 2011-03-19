"""The evaluators for the last.fm recommenders"""

from unresyst.recommender.evaluation import BaseEvaluator
from models import MovieEvaluationPair
from unresyst.recommender.metrics import rmse, precision_recall

class MovieRecommenderEvaluator(BaseEvaluator):
    """The evaluator of the artist recommender"""
    
    EvaluationPairModel = MovieEvaluationPair
    """The model - pairs"""
    
    prediction_metric = rmse
    """The metric"""
    
    recommendation_metric = precision_recall
    """The other metric"""

