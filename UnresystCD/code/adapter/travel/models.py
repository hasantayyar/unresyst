"""Models for the travel agency dataset"""

from django.db import models


from constants import *
from unresyst.models import BaseEvaluationPair

class User(models.Model):
    """The user"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return 'user_%d' % self.id   

class Session(models.Model):
    """User's session with the system"""
    
    user = models.ForeignKey('travel.User')
    """The user"""
    
    session_no = models.PositiveIntegerField()
    """The number of session for the user"""
    
    class Meta:
        unique_together = ('user', 'session_no')

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u'user %s: session: %d' % (self.user, self.session_no)
    
class Country(models.Model):
    """The country for a tour."""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    """The name of the country"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name  


class TourType(models.Model):
    """A model for a type of the tour."""    
        
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    """The name of the type."""    
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name     


class Tour(models.Model):
    """The tour"""    
    
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    """The name"""
    
    url = models.URLField(max_length=MAX_LENGTH_URL, verify_exists=False)
    """The url without the final id and without GET parameters"""
    
    country = models.ForeignKey('travel.Country')
    """The country the tour is to"""
    
    tour_type = models.ForeignKey('travel.TourType')
    """The type of the tour"""
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name     


class Action(models.Model):
    """An abstract class for a user action"""

    session = models.ForeignKey('travel.Session')
    """The session in which the action was taken (identifies the user)"""
    
    tour = models.ForeignKey('travel.Tour')
    """The tour on which the action was taken"""
    
    timestamp = models.DateTimeField()
    """The date and time the track was played"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"%s: %s" % (self.session.user, self.tour)
    
    class Meta:
        abstract = True    
        
class Order(Action):
    """User ordered a tour"""
    pass

class Question(Action):
    """User asked a question about a tour"""
    pass
    
class Click(Action):
    """User clicked on something on the tour profile"""
    pass
    
class MouseMove(Action):
    """User moved the mouse over something on the tour profile"""
    pass
    
class ViewProfile(Action):
    """User viewed the profile of the tour"""
    
    duration = models.PositiveIntegerField(null=True)
    """How long the user has been viewing the profile, 
    In seconds."""  
    

class TourOrderEvalPair(BaseEvaluationPair):
    """An abstract class for the artist evaluators"""

    subj = models.ForeignKey('travel.User')
    """The subject"""
    
    obj = models.ForeignKey('travel.Tour')
    """The object"""
    
    test_ratio = 0.2
    """The ratio of pairs to select to test pairs"""

    class Meta:
        app_label = 'travel' 
        
    @classmethod 
    def select(cls, i=0):
        """See the base class for the documentation."""  
              
        all_count = Order.objects.count()        
        test_count = int(cls.test_ratio * all_count )        
        train_count = all_count - test_count

        min_stamp_test = Order.objects.order_by('-timestamp')[test_count-1].timestamp

        test_pairs=Order.objects.filter(timestamp__gte=min_stamp_test)
        train_pairs = Order.objects.filter(timestamp__lt=min_stamp_test)
        
        # remove all other feedback newer than the test timestamp
        ViewProfile.objects.filter(timestamp__gt=min_stamp_test).delete()
        MouseMove.objects.filter(timestamp__gt=min_stamp_test).delete()
        Click.objects.filter(timestamp__gt=min_stamp_test).delete()
        Question.objects.filter(timestamp__gt=min_stamp_test).delete()
        
        # take 1/5 of the orders, remove them and put them to test data        
        # save to test, remove from build
        for order in test_pairs.iterator():

            # create the test pair for the order
            TourOrderEvalPair.objects.create(
                subj=order.session.user,
                obj=order.tour,
                expected_expectancy=EXPECTED_EXPECTANCY_ORDERED,
            )
                        
            
            # delete the order
            order.delete()
            
        print "%d test pairs selected from total %d pairs." % (test_count, all_count)          

    def get_success(self):
        return True
