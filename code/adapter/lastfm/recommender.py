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

class NovelArtistRecommender(Recommender):
    """A recommender for discovering previously unheard artists"""    

    name = "Novel Artist Recommender"
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

    """
    clusters:
    user:
     - country
     - gender
    """
     
    relationships = ()
    
    
    rules = (          
        # if users are the same age +- year they are similar
        SubjectSimilarityRule(
            name="Users with similar age.",
            
            # both users have given their age
            condition=lambda s1, s2: 
                s1.age and s2.age and abs(s1.age - s2.age) <= 5,
                
            is_positive=True,   
                
            weight=0.5,
            
            # a magic linear confidence function
            confidence=lambda s1, s2: 
                1 - float(abs(s1.age - s2.age))/AGE_DIFFERENCE,
            
            description="Users %(subject1)s and %(subject2)s are about " + 
                "the same age."
        ),        
        
        # if the users were registered in a similar period, the're similar
        SubjectSimilarityRule(
            name='Users registered in similar time.',
            
            condition=lambda s1, s2:
                s1.registered and s2.registered and \
                abs(s1.registered.toordinal() - s2.registered.toordinal()) < REGISTERED_DIFFERENCE / 5,
            
            is_positive=True,
            weight=0.5,
            
            confidence=lambda s1, s2:
                1 - float(abs(s1.registered.toordinal() - s2.registered.toordinal()))/REGISTERED_DIFFERENCE,
                
            description="Users %(subject1)s and %(subject2)s were registered in similar times",
        ),
    )
    
    cluster_sets = (
        # tag clusters
        ObjectClusterSet(

            name="Artist tags.",

            weight=0.5,
            
            # artists that are tagged by a tag that another artist also has
            filter_entities=Artist.objects.annotate(shared_count=Count('artisttag__tag__artisttag')).filter(shared_count__gt=1).distinct(),
            
            get_cluster_confidence_pairs=_get_artist_tag_pairs,
            
            description="%(object)s was tagged as %(cluster)s.",
        ),
        
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
            
            weight=0.5,
            
            # users that have country filled
            filter_entities=User.objects.filter(country__isnull=False),
            
            get_cluster_confidence_pairs=lambda user: ((user.country.name, 1),),
            
            description="%(subject)s is from %(cluster)s."
        ),
    )
    
    biases = (
        ObjectBias(
            name="Artists whose tracks were listened the most.",
            description="%(object)s is much listened.",
            weight=0.5,
            is_positive=True,
            # users whose tracks were listened more than the half of the most listened
            generator=lambda: Artist.objects.annotate(listen_count=Count('track__scrobble')).filter(listen_count__gt=MAX_SCROBBLE_COUNT/2),
            
            # the number of scrobbles for the artist divided by the max.
            confidence=lambda a: float(a.track_set.annotate(scrobble_count=Count('scrobble')).aggregate(Sum('scrobble_count')))/MAX_SCROBBLE_COUNT,
        ),
        
    )


    random_recommendation_description = "Recommending a random artist to the user."
    
    

class ArtistRecommender(NovelArtistRecommender):
    """A recommender for recommending items no matter if they were heard or not."""

    name = "Artist Recommender"
    """The name"""     
    
    remove_predicted_from_recommendations = False   
    """The already heard artists can appear in recommendations"""
    
    rules = NovelArtistRecommender.rules + ((SubjectObjectRule(
        name="User has listened to the artist.",
        condition=None,
        weight=0.5,
        is_positive=True,
        description="%(subject)s listened to %(object)s.",

        # the number of user's scrobbles on artist divided by the number of
        # user's scrobbles overall
        confidence=lambda s, o: 
            float(Scrobble.objects.filter(user=s, track__artist=o).count())\
                /Scrobble.objects.filter(user=s).count(),
        
        generator=_listens_artist_generator,
        )),
    )
      
