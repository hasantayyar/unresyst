"""The configuration for the last.fm recommender"""

from unresyst import *

from models import *

def _listens_artist_generator():
    """The generator to the predicted relationship"""
    for u in User.objects.iterator():
        for a in Artist.objects.filter(track__scrobble__user=u).distinct().iterator():
            yield (u, a)
    

class ArtistRecommender(Recommender):
    """A BaseRecommender subclass holding all domain-specific data"""

    name = "Artist Recommender"
    """The name"""    
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = Artist.objects
    """The objects that will be recommended.""" 

    predicted_relationship = PredictedRelationship( 
        name="User listens to artist's tracks.",
        condition=None, 
        description="""User %(subject)s listens to the %(object)s's tracks.""",
        generator=_listens_artist_generator
    )
    """The relationship that will be predicted"""
    
    relationships = ()
    """                              
        
        # if the users are of the same gender, they are similar
        # TODO pridat
        
        # if users are from the same country, they are considered similar
        SubjectSimilarityRelationship(
            name="Users are from the same country.",
            
            condition=lambda s1, s2:
                s1.country and s2.country and s1.country == s2.country, 
                
            is_positive=True,               
            
            weight=0.6,            
            
            description="Users %(subject1)s and %(subject2)s are from the same country."
        ),
                    
    )
    """
    """Relationships among the subjects and objects in the domain"""
    
    
    rules = ()       
    """    
        # if users are the same age +- year they are similar
        SubjectSimilarityRule(
            name="Users with similar age.",
            
            # both users have given their age
            condition=lambda s1, s2: 
                s1.age and s2.age and s1.age -1 <= s2.age <= s2.age + 1,
                
            is_positive=True,   
                
            weight=0.2,
            
            # a magic linear confidence function
            confidence=lambda s1, s2: 
                1 - 0.25 * abs(s1.age - s2.age),
            
            description="Users %(subject1)s and %(subject2)s are about " + 
                "the same age."
        ),
        
        # tags
        # TODO
        
    )
    """
    """Rules that can be applied to the domain"""

    random_recommendation_description = "Recommending a random artist to the user."
    
"""
ObjectSimilarityRule(
            name="Shoes with common keywords.",
            
            # shoes have some common keywords, if both empty, it's false
            condition=lambda o1, o2: 
                bool(_get_keyword_set(o1).intersection(_get_keyword_set(o2))),
            
            is_positive=True,
            
            weight=0.4,
            
            # the size of the intersection / the size of the smaller set
            confidence=_keyword_set_similarity,
            
            description="The shoe pairs %(object1)s and %(object2)s " + 
                "share some keywords."
        ),
"""        
