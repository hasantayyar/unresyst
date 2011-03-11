"""Models for the travel agency dataset"""

from django.db import models

from constants import *

class User(models.Model):
    """The user"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return 'user_%d' % self.id   

class Session(models.Model):
    """User's session with the system"""
    
    user = models.ForeignKey('travel.User')
    """The user"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u'user %s: session: %d' % (self.user, self.id)
    
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
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name"""
    
    url = models.URLField(max_length=MAX_LENGTH_URL, verify_exists=False)
    """The url without the final id and without GET parameters"""
    
    country = models.ForeignKey('travel.Country')
    """The country the tour is to"""
    
    tour_type = models.ForeignKey('travel.TourType')
    """The type of the tour"""

class Action(models.Model):
    """An abstract class for a user action"""

    session = models.ForeignKey('travel.Session')
    """The session in which the action was taken (identifies the user)"""
    
    tour = models.ForeignKey('travel.Tour')
    """The tour on which the action was taken"""
    
    timestamp = models.DateTimeField()
    """The date and time the track was played"""
    
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
    
    duration = models.TimeField(null=True)
    """How long the user has been viewing the profile, 
    for actions where page_close is missing it's null"""  
    
        
