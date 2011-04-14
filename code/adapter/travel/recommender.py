"""The configuration for the travel agency recommender"""
from django.db.models import Sum, Count, Avg

from unresyst import *

from models import *
from constants import *

def _viewed_profile_confidence(u, t):
    viewed_profs = ViewProfile.objects.filter(tour=t, session__user=u)
    view_count = viewed_profs.count()
    avg_duration = viewed_profs.aggregate(Avg('duration'))['duration__avg']
    
    return min((float(view_count)/6) * avg_duration/160, 1.0)

# predicted bude order
# remove_predicted_from_recommendations = True
# podpurny budou ty vtipy

class OrderTourRecommender(Recommender):
    """A recommender for suggesting what tour the user should order."""    

    name = "Order Tour Recommender"
    """The name"""    
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = Tour.objects
    """The objects that will be recommended.""" 

    random_recommendation_description = "Recommending a random tour to the user."

    predicted_relationship = PredictedRelationship( 
        name="User has ordered the tour.",
        condition=None, 
        description="""User %(subject)s has ordered %(object)s.""",
        generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) for uid, tid in Order.objects.values_list('session__user', 'tour').distinct()),        
    )
    """The relationship that will be predicted"""

     
    relationships = ()
    
    rules = (          
        # click = sign of preference
        SubjectObjectRule(
            name='User has clicked on something on the tour profile.',
            weight=0.05,
            condition=None,
            is_positive=True,
            description='User %(subject)s has clicked on something on the %(object)s profile.',
            # pairs that user has clicked on the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in Click.objects.values_list('session__user', 'tour').distinct()),
            # the average is around 3, so take 1/6. so that 3 points to the middle.
            confidence=lambda u, t: min(float(Click.objects.filter(tour=t, session__user=u).count())/6, 1.0),
        ),        
        
        # mouse move .. also a sign of preference
        SubjectObjectRule(
            name='User has moved the mouse on the tour profile.',
            weight=0.1,
            condition=None,
            is_positive=True,
            description='User %(subject)s has moved the mouse on %(object)s.',
            # pairs that user has moved on the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in MouseMove.objects.values_list('session__user', 'tour').distinct()),
            confidence=lambda u, t: min(float(MouseMove.objects.filter(tour=t, session__user=u).count())/18, 1.0),
        ),
        
        # view profile 
        SubjectObjectRule(
            name='User has viewed the tour profile page.',
            weight=0.1,
            condition=None,
            is_positive=True,
            description='User %(subject)s has viewed %(object)s.',
            # pairs that user has viewed the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in ViewProfile.objects.values_list('session__user', 'tour').distinct()),
            # how many times * how long
            confidence=_viewed_profile_confidence
        ),

       
    )
    

    biases = (
        # multiply viewed tours
        ObjectBias(
            name="Most viewed tours.",
            
            description="Tour %(object)s is much viewed",
            
            weight=0.3,
            
            is_positive=True,
            
            generator=lambda: Tour.objects.annotate(hh=Count('viewprofile')).filter(hh__gt=2).distinct(),
            
            confidence=lambda t: min(float(t.viewprofile_set.count())/4, 1.0)
        ),
                
        
        # multiply mouse moved tours
        ObjectBias(
            name="Most mouse moved tours.",
            
            description="Tour %(object)s is often mouse moved.",
            
            weight=0.2,
            
            is_positive=True,
            
            generator=lambda: Tour.objects.annotate(hh=Count('mousemove')).filter(hh__gt=6).distinct(),
            
            confidence=lambda t: min(float(t.mousemove_set.count())/12, 1.0)
        ),
        # multiply clicked tours
        ObjectBias(
            name="Most clicked tours.",
            
            description="Tour %(object)s is often clicked on.",
            
            weight=0.5,
            
            is_positive=True,
            
            generator=lambda: Tour.objects.annotate(hh=Count('click')).filter(hh__gt=1).distinct(),
            
            confidence=lambda t: min(float(t.click_set.count())/2, 1.0)
        ),
        
    )



    

