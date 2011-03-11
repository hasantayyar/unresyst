"""Models for the flixster app"""
from django.db import models

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
    """A user is a friend of another user. Symmetric."""

    friend1 = models.ForeignKey('flixster.User', related_name='friends1')
    """The first user in the friend relationship"""        
    
    friend2 = models.ForeignKey('flixster.User', related_name='friends2')
    """The second user in the friend relationship"""            

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

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u'%s - %s: %f' % (self.user, self.movie, self.rating)
            
        
