"""An example of an Unresyst recommender for the last.fm domain.
The addaptation rules include:
 - subject-object preference 
 - subject-subject similarity
 - object-object similarity
 - object bias

Recommenders used during the evaluation tests can be found in:
 - lastfm/recommender.py
 - travel/recommender.py
 - flixster/recommender.py
"""

from unresyst import *
from models import *

AGE_DIFFERENCE = 38 - 17
"""The age difference between the oldest and the yongest user"""

MAX_PLAY_COUNT = 542
"""The maximum play count for an artist in the period"""

N_MIN_PLAY_COUNT = 100
"""The minimum play count for an artist to apply the bias"""

PERIOD_START_DATE = datetime.date(2010, 9, 1)
PERIOD_END_DATE = datetime.date(2010, 12, 31)


class ArtistRecommender(Recommender):
    """A recommender recommending artists (musicians) that 
    the user can like.
    """    
    
    name = " Artist Recommender"
    """The name"""    
    
    subjects = User.objects
    """The subjects to who the recommender will recommend."""
    
    objects = Artist.objects
    """The objects that will be recommended."""
    
    predicted_relationship = PredictedRelationship( 
        name="User listens to artist's tracks.",
        
        # gives true for user, artist pairs where the user have listened
        # to the artist
        condition=lambda user, artist: \
            user.scrobble_set.filter(track__artist=artist).exists(), 
        
        description="""User %(subject)s listens to the %(object)s's tracks."""
    )
    """The relationship that will be predicted"""
    
    # the class contains definitions for business rules
    rules = (
    
        # don't recommend artists with male-specific tags to females
        SubjectObjectRule(
            name="Don't recommend male music to female users.",

            # the user is a female and the artist was tagged by
            # a male-specific tag
            condition=lambda user, artist: user.gender == 'f' and \
                artist.artisttag_set.filter(tag__gender_specific='m').exists(),
            
            # it's a negative rule
            is_positive=False,
            
            weight=0.5,
            
            # the more male-specific tags the artist has, the higher is 
            # the rule confidence. Normalized by the artist tag count
            confidence=lambda user, artist: float(
                artist.artisttag_set.filter(tag__gender_specific='m').count())/ \
                    artist.artisttag_set.count(),
                    
            description="Artist %(object)s isn't recommended to %(subject)s, " +
                "because the artist is considered male-specific."
        ),
                
                
        # users of similar age are similar
        SubjectSimilarityRule(
            name="Users with similar age.",
            
            # both users have given their age and the difference 
            # is lower than five
            condition=lambda user1, user2: 
                user1.age and user2.age and abs(user1.age - user2.age) <= 5,
                
            is_positive=True,   
                
            weight=0.5,
            
            # a magic linear confidence function
            confidence=lambda user1, user2: 
                1 - float(abs(user1.age - user2.age))/AGE_DIFFERENCE,
            
            description="Users %(subject1)s and %(subject2)s are about " + 
                "the same age."
        ),        
        
        # artists sharing some tags are similar
        ObjectSimilarityRule(
            name="Artists sharing some tags.",

            # both artists have some tags and they share at least one tag
            condition=lambda artist1, artist2: \
                artist1.artisttag_set.exists() and \
                artist2.artisttag_set.exists() and \
                artist1.artisttag_set.filter(
                    tag__id__in=artist2.artisttag_set.values_list('tag__id')
                ).exists(),
            
            # it's a positive rule
            is_positive=True,
            
            weight=0.5,
            
            # The more tags the artists have in common, the higher is  
            # the similarity confidence
            confidence=lambda artist1, artist2: \
                float(artist1.artisttag_set.filter(
                    tag__id__in=artist2.artisttag_set.values_list('tag__id')
                ).count()) / \
                min(artist1.artisttag_set.count(), artist2.artisttag_set.count()),
            
            description="Artists %(object1)s and %(object2)s are similar " +
             "because they share some tags."
        ),
    )
    
    relationships = (
        # if two users are from the same country, they are similar
        SubjectSimilarityRelationship(
            name="Users living in the same country",
            
            # both users have given their country and it's the same
            condition=lambda user1, user2:
                user1.country and \
                user2.country and \
                user1.country == user2.country,
            
            # it's relationship positive to similarity
            is_positive=True,               
            
            weight=0.5,            
            
            description="Users %(subject1)s and %(subject2)s are from " + \
            " the same country.",
        ),
    )
    
    biases = (
        ObjectBias(
            name="Artists whose tracks have been listened a lot recently.",
            
            description="%(object)s has been listened much recently.",
            
            # take only artists with more than the minimal play count
            # in the given period
            condition=lambda artist: \
                artist.track_set\
                    .filter(scrobble__timestamp__range=
                        (PERIOD_START_DATE, PERIOD_END_DATE))\
                    .aggregate(Count('scrobble')) > N_MIN_PLAY_COUNT,
            
            weight=0.5,
            
            # it's a positive bias
            is_positive=True,
            
            # the number of scrobbles for the artist divided by the max.
            confidence=lambda artist: \
                float(artist.track_set\
                    .filter(scrobble__timestamp__range=
                        (PERIOD_START_DATE, PERIOD_END_DATE))\
                    .annotate(scrobble_count=Count('scrobble'))\
                    .aggregate(Sum('scrobble_count')))/MAX_PLAY_COUNT
        ),
    )
