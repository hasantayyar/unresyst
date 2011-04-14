"""Saving data from the last.fm datasets"""

import csv
import os
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc

from models import *

TZ = tzutc()
"""The used timezone"""

GENDER_SPECIFIC_TAGS = {
    'punk': 'm',
    'metal': 'm',
    'punk rock': 'm',
    'hardcore': 'm',
    'hard rock': 'm',
    'industrial': 'm',
    'post-punk': 'm',
    'post-rock': 'm',
    'heavy metal': 'm',
    'metalcore': 'm',
    'death metal': 'm',
    'noise': 'm',
    'hardcore punk': 'm',

    'female': 'f',
    'beautiful': 'f',
    'Love': 'f',
    'lovely': 'f',
    'sweet': 'f',
    'singer-songwriter': 'f',
    'singer songwriter': 'f',
    'woman': 'f',
    'mellow': 'f',
    'dream pop': 'f',
    'soft': 'f',
    'emotional': 'f',
    'cut': 'f',
}
"""Tags that are specific for the given gender.
"""

"""
7141 artists
992 users
19903 tracks
22666 scrobbles



# relative paths to the dataset files
filename_scrobbles =  '../../datasets/lastfm/1K/tracks30000.tsv'
filename_users = '../../datasets/lastfm/1K/userid-profile.tsv'
filename_tags = '../../datasets/lastfm/Lastfm-ArtistTags2007/artist_tags200K.tsv'
"""

"""
2348 artists
100 users
5057 tracks
5532 scrobbles
9120 tags
28588 tagartists
322 tagged artists

max age 38
min age 17
"""
# relative paths to the dataset files
filename_scrobbles =  '../../datasets/lastfm/mini/scrobbles.tsv'
filename_users = '../../datasets/lastfm/mini/users.tsv'
filename_tags = '../../datasets/lastfm/mini/tags.tsv'

separator = '\t'

def save_data():
    """Save the data"""
    _parse_users(filename_users)
    print "Users saved."
    
    _parse_scrobbles(filename_scrobbles)
    print "Scrobbles saved."
    
    _parse_tags(filename_tags)
    print "Tags saved."

"""
user_000001	m		Japan	Aug 13, 2006
user_000002	f		Peru	Feb 24, 2006
user_000003	m	22	United States	Oct 30, 2005
"""

def _parse_users(filename):
    """Parse the user csv file"""
    
    filename = _get_abs_path(filename)

    # open the csv reader
    reader = csv.reader(open(filename, "rb"), delimiter=separator, quoting=csv.QUOTE_NONE)
    
    for user_id, gender, age, country, reg_date in reader:
        
        # parse the user id
        user_id = _parse_user_id(user_id)
        
        # replace the empty string by None
        age = None if not age else age
        
        # find or create the country
        if country:
            country_model, created = Country.objects.get_or_create(name=country)
        else:
            country_model = None
        
        # parse the date
        reg_date = None if not reg_date else datetime.strptime(reg_date, '%b %d, %Y')
        
        # create and save the user
        user = User(
            id=user_id,
            gender=gender,
            age=age,
            country=country_model,
            registered=reg_date)
        
        user.save()

"""
 user_000639  2009-04-08T01:57:47Z  15676fc4-ba0b-4871-ac8d-ef058895b075  The Dogs D'Amour  6cc252d0-3f42-4fd3-a70f-c8ff8b693aa4  How Do You Fall in Love Again
"""

def _parse_scrobbles(filename):
    """Parse the scrobbles by the users"""

    filename = _get_abs_path(filename)
    
    reader = csv.reader(open(filename, "rb"), delimiter=separator, quoting=csv.QUOTE_NONE)
    for user_id, timestamp, artist_guid, artist_name, track_guid, track_name in reader:

        if reader.line_num % 1000 == 0:
            print '%s lines processed' % reader.line_num  
                    
        # if the track isn't in the musicbrainz db, continue
        if not track_guid or not artist_guid:
            continue
        
        # parse the user id and find the user
        user_id = _parse_user_id(user_id)
        user = User.objects.get(id=user_id)
        
        # parse the date and put it to the UTC timezone
        timestamp = parse(timestamp).astimezone(TZ).replace(tzinfo=None)
        
        # get or create the artist
        artist, created = Artist.objects.get_or_create(
                            guid=artist_guid,
                            defaults={'name': artist_name})
        
        # get or crate the track
        track, created = Track.objects.get_or_create(
                            guid=track_guid, 
                            defaults= {'artist': artist, 'name': track_name})
                            
        
        # create and save the scrobble
        scrobble = Scrobble(
            user=user,
            timestamp=timestamp,
            track=track)
            
        scrobble.save()  
              

"""
    11eabe0c-2638-4808-92f9-1dbd9c453429<sep>Deerhoof<sep>american<sep>14
    11eabe0c-2638-4808-92f9-1dbd9c453429<sep>Deerhoof<sep>animals<sep>5
    11eabe0c-2638-4808-92f9-1dbd9c453429<sep>Deerhoof<sep>art punk<sep>2
"""    

def _parse_tags(filename):
    """Parse the tags"""

    filename = _get_abs_path(filename)
    
    reader = csv.reader(open(filename, "rb"), delimiter=separator, quoting=csv.QUOTE_NONE)
    
    last_artist = Artist.objects.all()[0]
    
    for artist_guid, artist_name, tag_name, count in reader:

        if reader.line_num % 1000 == 0:
            print '%s lines processed' % reader.line_num 
                
        # some caching for more speed
        if artist_guid == last_artist.guid:
            artist = last_artist
        else:                    
            # try finding the artist
            qs_artist = Artist.objects.filter(guid=artist_guid)
            
            # if not found go ahead
            if not qs_artist:
                continue
            
            artist = qs_artist[0]
        
        # if the name is strange, go ahead
        if artist.name != artist_name:
            continue
        
        # get the gender specificity
        if GENDER_SPECIFIC_TAGS.has_key(tag_name):
            gender_specific = GENDER_SPECIFIC_TAGS[tag_name]
        else:
            gender_specific = ''
        
        # get or create the tag
        tag, created = Tag.objects.get_or_create(
            name=tag_name, 
            defaults={'gender_specific': gender_specific,})        
        
        # create and save the tag for the artist 
        artist_tag = ArtistTag(
                        artist=artist,
                        tag=tag,
                        count=count)
                        
        artist_tag.save()   
        
        last_artist = artist                    
        
        
def _get_abs_path(filename):
    """Get the absolute path from the relative"""
    return os.path.join(os.path.dirname(__file__), filename)
    
def _parse_user_id(user_id):
    """Get the integer id from the id string"""
    return int(user_id.split('_')[1])
