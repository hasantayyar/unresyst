"""The models for the last.fm datasets."""


"""
user_000001	2009-05-04T23:08:57Z	f1b1cf71-bd35-4e99-8624-24a6e15f133a	Deep Dish		Fuck Me Im Famous (Pacha Ibiza)-09-28-2007
user_000001	2009-04-01T14:24:52Z	6c639b1f-5390-4ec9-b3f8-7afe1562e107	Lady Alma		Running For Nothing [(Instrumental)]/(Instrumental)
user_000001	2009-02-05T22:58:19Z	440cb8ef-cee3-4711-8408-b1bd6e93f390	Towa Tei	c605c224-245b-4107-b9cd-ab1b2c6adb0a	Mind Wall (Feat. Miho Hatori)

#id	gender	age	country	registered
user_000001	m		Japan	Aug 13, 2006
user_000002	f		Peru	Feb 24, 2006
user_000003	m	22	United States	Oct 30, 2005
user_000004	f			Apr 26, 2006
user_000005	m		Bulgaria	Jun 29, 2006
user_000006		24	Russian Federation	May 18, 2006
user_000007	f		United States	Jan 22, 2006
user_000008	m	23	Slovakia	Sep 28, 2006
user_000009	f	19	United States	Jan 13, 2007
user_000010	m	19	Poland	May 4, 2006
user_000011	m	21	Finland	Sep 8, 2005
"""

from django.db import models

from unresyst.models import ValidationPair

from constants import *

class User(models.Model):
    """The user"""
    
    gender = models.CharField(max_length=1)
    """The english name of the enumerator. Should be translated by ugettext before 
    displaying."""
    
    age = models.PositiveIntegerField(null=True, default=None)
    """The age of the user."""
    
    registered = models.DateTimeField(null=True, default=None)
    """Date when the user was registered"""

    country = models.ForeignKey('Country', null=True)
    """The country the user is from"""    

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return 'user_%d' % self.id        
    
    
class Country(models.Model):
    """A model for a country."""    
        
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    """The name of the city."""    
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name        
  
        
class Track(models.Model):
    """A track (song)"""
    
    guid = models.CharField(primary_key=True, max_length=40)
    """The id of the track in the musicbrainz database"""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name of the track."""

    artist = models.ForeignKey('Artist')
    """The author of the track"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"%s: %s" % (self.artist, self.name)


class Artist(models.Model):
    """An artist (band or singer)"""
    
    guid = models.CharField(primary_key=True, max_length=40)
    """The id of the singer in the musicbrainz database"""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    """The name of the track."""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name  


class Scrobble(models.Model):
    """A representation of the fact that a user has played a track"""
    
    user = models.ForeignKey('User')
    """The user"""
    
    track = models.ForeignKey('Track')
    """The played track"""
    
    timestamp = models.DateTimeField()
    """The data and time the track was played"""
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"(%s, %s)" % (self.user, self.track)


class ArtistTag(models.Model):
    """A representation a artist being tagged by the tag"""
    
    artist = models.ForeignKey('Artist')
    """The artist"""
    
    tag = models.ForeignKey('Tag')
    """The tag"""    
    
    count = models.PositiveIntegerField()
    """How many times the artist was tagged by the tag"""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"(%s, %s: %d)" % (self.artist, self.tag, self.count)    
    

    
class Tag(models.Model):
    """A representation of a tag (label) in the system"""
    
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    """The label."""

    def __unicode__(self):
        """Return a printable representation of the instance"""
        return self.name     

        
class ArtistRecommenderValidationPair(ValidationPair):
    """An artist - user pair for validation purposes"""
    
    subj = models.ForeignKey('lastfm.User')
    """The subject"""
    
    obj = models.ForeignKey('lastfm.Artist')
    """The object"""
    
    def __unicode__(self):
        """Return a printable representation of the instance"""
        return u"%s - %s" % (self.subj, self.obj)

    @classmethod
    def select_validation_pairs(cls, i=0):
        """See the base class for the documentation."""

        scrobble_count = Scrobble.objects.all().count()
        
        # get a queryset containing every n-th scrobble
        id_list = range(1 + i, scrobble_count, CROSS_VALIDATION_COUNT)
        qs_validation_scrobbles = Scrobble.objects.filter(id__in=id_list)
        
        # remove the scrobbles and add them to the class
        for scrobble in qs_validation_scrobbles.iterator():
            
            # create and save the validation pair
            val_pair = cls(
                subj=scrobble.user,
                obj=scrobble.track.artist,
                expected_expectancy=EXPECTED_EXPECTANCY_LISTENED)                
            val_pair.save()
            
            # remove the scrobble
            scrobble.delete()


    def get_success(self):
        """See the base class for the documentation."""
        return self.obtained_expectancy > SUCCESS_LIMIT

