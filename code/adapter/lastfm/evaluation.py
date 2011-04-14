"""The evaluators for the last.fm recommenders"""

from unresyst.recommender.evaluation import BaseEvaluator
from unresyst.recommender.rank_evaluation import RankEvaluator
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
    
class ArtistRankEvaluator(RankEvaluator):
    """Evaluating the rank metric"""
    
    EvaluationPairModel = ArtistEvalPair
    """The model - pairs"""
    
    SUBJ_IDS = [
        6L,
        11L,
        14L,
        36L,
        38L,
        53L,
        55L,
        59L,
        61L,
        79L,
        81L,
        90L,
    ]

    
class NovelArtistRecommenderEvaluator(BaseEvaluator):
    """The evaluator of the novel artist recommender"""
    
    EvaluationPairModel = NovelArtistEvalPair
    
    prediction_metric = rmse
    
    recommendation_metric = precision_recall    

    
class NovelArtistRankEvaluator(RankEvaluator):
    """Evaluation of the rank metric"""
    
    EvaluationPairModel = NovelArtistEvalPair
    """The model - pairs"""
    
    SUBJ_IDS = ArtistRankEvaluator.SUBJ_IDS
