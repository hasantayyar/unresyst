"""The evaluators for the last.fm recommenders"""

from unresyst.recommender.evaluation import BaseEvaluator
from models import ArtistEvalPair, NovelArtistEvalPair
from unresyst.recommender.metrics import rmse, precision_recall

class ArtistRecommenderEvaluator(BaseEvaluator):
    """The evaluator of the artist recommender"""
    
    EvaluationPairModel = ArtistEvalPair
    """The model - pairs"""
    
    prediction_metric = rmse
    """The metric"""
    
    recommendation_metric = precision_recall
    """The other metric"""
    
class NovelArtistRecommenderEvaluator(BaseEvaluator):
    """The evaluator of the novel artist recommender"""
    
    EvaluationPairModel = NovelArtistEvalPair
    
    prediction_metric = rmse
    
    recommendation_metric = precision_recall    
