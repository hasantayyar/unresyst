"""The recommender used in the parent system 
(the unresyst.Recommender subclass)
"""

from unresyst import *

from models import *

class MySpecificRecommender(Recommender):
    """A Recommender subclass holding all domain-specific data"""
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = ShoePair.objects
    """The objects that will be recommended.""" 

    relationship = Relationship( \
        condition=lambda s, o: o in s.shoes.all(), \
        description="""User %(subject)s has shoes %(object)s).""")
    """The relationship that will be predicted"""
    
    #rules = ...
