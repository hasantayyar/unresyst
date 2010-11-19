"""The recommender used in the parent system 
(the unresyst.BaseRecommender subclass)
"""

from unresyst import *

from models import *

class ShoeRecommender(Recommender):
    """A BaseRecommender subclass holding all domain-specific data"""
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = ShoePair.objects
    """The objects that will be recommended.""" 

    predicted_relationship = Relationship( \
        condition=lambda s, o: o in s.shoes.all(), \
        description="""User %(subject)s likes shoes %(object)s).""")
    """The relationship that will be predicted"""
    
    relationships = (,
    )
    """Relationships among the subjects and objects in the domain"""
    
    
    rules = (,    
    )
    """Rules that can be applied to the domain"""
    

