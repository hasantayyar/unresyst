"""The flixster recommender"""

from django.db.models import Avg

from unresyst import *
from models import *
from constants import *

def _rated_positively_generator():
    """The generator to the predicted relationship"""
    for r in Rating.objects.filter(rating__gt=str(MIN_POSITIVE_RATING)):
        yield (r.user, r.movie)

class MovieRecommender(Recommender):
    """The flixster movie recommender"""

    name = "Flixster Movie Recommender"
    """The name"""    
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = Movie.objects
    """The objects that will be recommended.""" 

    predicted_relationship = PredictedRelationship( 
        name="User has rated the movie positively.",
        condition=None, 
        description="""User %(subject)s has rated the %(object)s positively.""",
        generator=_rated_positively_generator,
    )
    """The relationship that will be predicted"""
    
    rules = (
        # explicit rating
        ExplicitSubjectObjectRule(
            name="Movie rating.",
            
            description="User %(subject)s has rated %(object)s.",
            
            # all pairs user, rated movie
            generator=lambda: [(r.user, r.movie) for r in Rating.objects.all()],
            
            # the number of stars divided by five
            expectancy=lambda s, o:float(Rating.objects.get(user=s, movie=o).rating) / MAX_STARS,
        ),
    )
    """The rules"""

    relationships = (
        # users in friendship
        SubjectSimilarityRelationship(
            name="Users are friends.",
            
            generator=lambda: [(f.friend1, f.friend2) for f in Friend.objects.all()], 
            
            is_positive=True,               
            
            weight=0.65,            
            
            description="Users %(subject1)s and %(subject2)s are friends.",
        ),
    )
    """The relationships"""
        
    biases = (
                
        # people giving high ratings
        SubjectBias(
            name="Users giving high ratings.",
            
            description="User %(subject)s gives high ratings.",
            
            weight=1.0,           
            
            is_positive=True,
            
            generator=lambda: User.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__gt=str(MIN_HIGH_RATING)),            
            
            confidence=lambda user: user.rating_set.aggregate(Avg('rating'))['rating__avg'] - MIN_HIGH_RATING
        ),
        
        # highly rated movies
        ObjectBias(
            name="High-rated movies.",
            
            description="Movie %(object)s is high-rated",
            
            weight=1.0,
            
            is_positive=True,
            
            generator=lambda: Movie.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__gt=str(MIN_HIGH_RATING)),
            
            confidence=lambda movie: movie.rating_set.aggregate(Avg('rating'))['rating__avg'] - MIN_HIGH_RATING
        ),
        
        # people giving low ratings
        SubjectBias(
            name="Users giving low ratings.",
            
            description="User %(subject)s gives low ratings.",
            
            weight=0.25,           
            
            is_positive=False,
            
            generator=lambda: User.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__lt=str(MAX_LOW_RATING)),            
            
            confidence=lambda user: MAX_LOW_RATING - user.rating_set.aggregate(Avg('rating'))['rating__avg'] 
        ),
        
        # low-rated movies
        ObjectBias(
            name="Low-rated movies.",
            
            description="Movie %(object)s is low-rated",
            
            weight=0.25,
            
            is_positive=False,
            
            generator=lambda: Movie.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__lt=str(MAX_LOW_RATING)),
            
            confidence=lambda movie: MAX_LOW_RATING - movie.rating_set.aggregate(Avg('rating'))['rating__avg']
        ),        
                
    
    )
    
    
