"""Models for the flixster app"""
from django.db import models
from django.db.models import Min

from unresyst.models import BaseEvaluationPair
from constants import *

class User(models.Model):
    """The user"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return 'user_%d' % self.id        
        
        
class Movie(models.Model):        
    """The movie"""
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return 'movie_%d' % self.id        

        
class Friend(models.Model):
    """A user is a friend of another user. Symmetric. Smaller id first."""

    friend1 = models.ForeignKey('flixster.User', related_name='friends1')
    """The first user in the friend relationship"""        
    
    friend2 = models.ForeignKey('flixster.User', related_name='friends2')
    """The second user in the friend relationship"""   
    
    class Meta:
        unique_together = ('friend1', 'friend2')         

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u'(%s, %s)' % (self.friend1, self.friend2)

    
class Rating(models.Model):
    """A user rating a movie"""
    
    user = models.ForeignKey('flixster.User')
    """The user"""
    
    movie = models.ForeignKey('flixster.Movie')
    """The movie"""
    
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    """The rating"""

    class Meta:
        unique_together = ('user', 'movie')

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u'%s - %s: %f' % (self.user, self.movie, self.rating)


class MovieEvaluationPair(BaseEvaluationPair):
    """Movie test pairs"""

    subj = models.ForeignKey('flixster.User')
    """The subject"""
    
    obj = models.ForeignKey('flixster.Movie')
    """The object"""
    
    test_ratio = 0.2
    """The ratio of pairs to select to test pairs"""

    class Meta:
        app_label = 'flixster'   
        
    @classmethod 
    def select(cls, i=0):
        """See the base class for the documentation."""

        n = int(1 / cls.test_ratio)        
        all_count = Rating.objects.count()                        
        
        it = 0        
        # take every n-th rating, remove it and put it to test data        
        # save to test, remove from build
        for rating in Rating.objects.order_by('id').iterator():

            it += 1

            # if we aren't on the nth object go ahead
            if it % n != i:
                continue
            
            # save the test object and delete it from train
            cls.objects.create(
                subj=rating.user,
                obj=rating.movie,
                expected_expectancy=rating.rating/MAX_STARS)
            
            rating.delete()
                
            
        test_count = cls.objects.count()
        
        print "%d test pairs selected from total %d pairs" % (test_count, all_count)          


    def get_success(self):
        """See the base class for the documentation."""
        return abs(self.obtained_expectancy - self.expected_expectancy) < MAX_TOLERANCE / MAX_STARS
    
         
        
