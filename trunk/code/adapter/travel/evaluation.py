"""The evaluators for the last.fm recommenders"""

from unresyst.recommender.evaluation import BaseEvaluator
from models import TourOrderEvalPair
from unresyst.recommender.metrics import rmse, precision_recall

class OrderTourRecommenderEvaluator(BaseEvaluator):
    """The evaluator of the artist recommender"""
    
    EvaluationPairModel = TourOrderEvalPair
    """The model - pairs"""
    
    prediction_metric = rmse
    """The metric"""
    
    recommendation_metric = precision_recall
    """The other metric"""

