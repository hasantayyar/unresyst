"""A package holding the whole unresyst application.

The only class to be used outside is the BaseRecommender.
"""

from recommender.recommender import Recommender
from recommender.rules import *
from recommender.clusters import *
from recommender.bias import *
