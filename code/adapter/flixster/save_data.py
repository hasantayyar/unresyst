"""Saving data from csv files"""
import csv
import os

from django.db.models import Count

from models import *

# relative paths to the dataset files
filename_links =  '../../datasets/flixster/mini/links.tsv'
filename_ratings = '../../datasets/flixster/mini/ratings.tsv'

separator = '\t'

"""
Before the removal:

>>> User.objects.count()
1269
>>> Friend.objects.count()
4439
>>> Movie.objects.count()
4237
>>> Rating.objects.count()
14195

After the removal:

>>> User.objects.count()
418
>>> Friend.objects.count()
1051

"""

max_user_id = 1520

def _get_abs_path(filename):
    """Get the absolute path from the relative"""
    return os.path.join(os.path.dirname(__file__), filename)

def save_data():
    """Save the data"""
    _parse_links(filename_links)
    print "Users and links saved."
    
    _parse_ratings(filename_ratings)
    print "Ratings saved."    
    
    # remove things we don't like
    
    # remove users without rating - they can't be tested anyhow    
    User.objects.annotate(rating_count=Count('rating')).filter(rating_count=0).delete()
    print "Disliked stuff deleted." 


"""
6	1349
6	1370
6	1375
6	1761
6	1770
6	1775
6	1785
6	1797
6	1803
6	1810
6	1819
6	1825
6	1831
"""    
    
def _parse_links(filename):
    """Parse the user csv file"""
    
    filename = _get_abs_path(filename)
    
    last_user = User(id=0)    

    # open the csv reader
    reader = csv.reader(open(filename, "rb"), delimiter=separator, quoting=csv.QUOTE_NONE)
    
    for user_id, friend_id in reader:
        
        if reader.line_num % 5000 == 0:
            print '%s lines processed' % reader.line_num  
            
        # parse the user ids
        user_id = int(user_id)
        friend_id = int(friend_id)        
        
        # skip high friends
        if friend_id > max_user_id:
            continue
        
        # if it's about the last user, use him, otherwise create him
        if user_id == last_user.id:            
            user = last_user
        else:
            user, created = User.objects.get_or_create(id=user_id)
        
        # get or create the friend
        friend, created = User.objects.get_or_create(id=friend_id)                
        
        f1, f2 = (user, friend) if user.id < friend.id else (friend, user)
        
        # create the friendship
        Friend.objects.get_or_create(
            friend1=f1,
            friend2=f2)
        
        # save the user for the next time
        last_user = user
"""
6	57699	3
7	18858	4
8	20644	4
8	43310	4
8	5806	4
9	33430	4
11	12145	4
11	12913	3
11	12920	5
11	14034	3.5
11	14277	4
11	14506	4
11	14889	5
11	15154	3.5
11	15815	5
11	16476	4.5
11	18181	5
11	18874	5
"""

def _parse_ratings(filename):
    """Parse the user csv file"""

    filename = _get_abs_path(filename)
    
    last_user = User(id=0)    

    # open the csv reader
    reader = csv.reader(open(filename, "rb"), delimiter=separator, quoting=csv.QUOTE_NONE)
    
    for user_id, movie_id, rating  in reader:
        
        if reader.line_num % 1000 == 0:
            print '%s lines processed' % reader.line_num  
            
        # parse the ids and rating
        user_id = int(user_id)
        movie_id = long(movie_id)   
        rating = rating

        # if it's about the last user, use him, otherwise get him
        if user_id == last_user.id:            
            user = last_user
        else:
            # take only users we already have
            user = User.objects.filter(id=user_id)        
            if not user:
                continue
            
            user=user[0]
        
        # get or create the movie
        movie, created = Movie.objects.get_or_create(id=movie_id)
        
        # create the rating
        Rating.objects.create(
            user=user, 
            movie=movie,
            rating=rating)
        
        # save the user for the next time
        last_user = user
        
