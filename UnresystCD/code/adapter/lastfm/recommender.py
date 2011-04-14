"""The configuration for the last.fm recommender"""
from django.db.models import Sum, Count

from unresyst import *

from models import *
from constants import *


AGE_DIFFERENCE = 38 - 17

REGISTERED_DIFFERENCE = 733696 - 731857

MAX_SCROBBLE_COUNT = 85

SCROBBLE_DIFFERENCE = MAX_SCROBBLE_COUNT - 1

def _listens_artist_generator():
    """The generator to the predicted relationship"""
    for u in User.objects.iterator():
        for a in Artist.objects.filter(track__scrobble__user=u).distinct().iterator():
            yield (u, a)

def _get_artist_tag_pairs(artist):
    """Get list tags, confidence for all tags he/she has"""    
        
    sumcount = artist.artisttag_set.aggregate(Sum('count'))['count__sum']
    
    # get only tags that are shared between at least two artists    
    artist_tags = artist.artisttag_set.annotate(tagcount=Count('tag__artisttag')).filter(tagcount__gt=1)

    # confidence is counted as 
    # the count of the tag / how many times the artist was tagged.
    return [(at.tag.name, float(at.count)/sumcount) \
        for at in artist_tags]

def _tag_similarity_generator():
    """Generate the pairs that share some tags"""
    
    # the artists that were tagged at least once
    qs_tagged_artists = Artist.objects.filter(artisttag__isnull=False).distinct()
    count = qs_tagged_artists.count()
    
    for a1, count in zip( qs_tagged_artists[1:].iterator(), \
            range(1, count)):

        # obtain only first count entities
        for a2 in qs_tagged_artists[:count].iterator():
            if a1.artisttag_set.filter(
                    tag__id__in=a2.artisttag_set.values_list('tag__id')
                ).distinct().count() > 45:
                yield (a1, a2)  

def _gender_specific_generator():
    """Generate pairs for the gender-specific tag rule"""
    
    qs_tagged_artists = Artist.objects.filter(artisttag__tag__gender_specific='m').distinct()
    
    for a in qs_tagged_artists:
        for u in User.objects.filter(gender='f'):
            yield (u, a)

class NovelArtistRecommender(Recommender):
    """A recommender for discovering previously unheard artists"""    

    name = "Novel Artist Recommender"
    """The name"""    
    
    subjects = User.objects
    """The subjects to who the recommender will recommend."""
    
    objects = Artist.objects
    """The objects that will be recommended.""" 

    predicted_relationship = PredictedRelationship( 
        name="User listens to artist's tracks.",
        condition=None, 
        description="""User %(subject)s listens to the %(object)s's tracks.""",
        generator=_listens_artist_generator
    )
    """The relationship that will be predicted"""

    """
    clusters:
    user:
     - country
     - gender
    """
     
    relationships = ()
    
    rules = (
       # users of similar age are similar
        SubjectSimilarityRule(
            name="Users with similar age.",
            
            # both users have given their age and the difference 
            # is lower than five
            condition=lambda user1, user2: 
                user1.age and user2.age and abs(user1.age - user2.age) <= 5,
                
            is_positive=True,   
                
            weight=0.4,
            
            # a magic linear confidence function
            confidence=lambda user1, user2: 
                1 - float(abs(user1.age - user2.age))/AGE_DIFFERENCE,
            
            description="Users %(subject1)s and %(subject2)s are about " + 
                "the same age."
        ),        
    )   

    cluster_sets = (

        
        # user - gender
        SubjectClusterSet(
            
            name='User gender.',
            
            weight=0.5,
            
            # users that have a gender (filled)
            filter_entities=User.objects.exclude(gender=''),
            
            get_cluster_confidence_pairs=lambda user: ((user.gender, 1),),
            
            description="%(subject)s's gender is %(cluster)s."
        
        ),
        
        # user - country
        SubjectClusterSet(
            
            name='User country.',
            
            weight=0.1,
            
            # users that have country filled
            filter_entities=User.objects.filter(country__isnull=False),
            
            get_cluster_confidence_pairs=lambda user: ((user.country.name, 1),),
            
            description="%(subject)s is from %(cluster)s."
        ),
    )
    
    save_all_to_predictions = True

    random_recommendation_description = "Recommending a random artist to the user."
    
    

class ArtistRecommender(NovelArtistRecommender):
    """A recommender for recommending items no matter if they were heard or not."""

    name = "Artist Recommender"
    """The name"""     
    
    remove_predicted_from_recommendations = False   
    """The already heard artists can appear in recommendations"""
    
    rules = NovelArtistRecommender.rules + ((SubjectObjectRule(
        name="User has listened to the artist.",
        generator=_listens_artist_generator,
        weight=0.5,
        is_positive=True,
        description="%(subject)s listened to %(object)s.",

        # the number of user's scrobbles on artist divided by the number of
        # user's scrobbles overall
        confidence=lambda s, o: 
            float(Scrobble.objects.filter(user=s, track__artist=o).count())\
                /Scrobble.objects.filter(user=s).count(),
        
        
        )),
    )
      
