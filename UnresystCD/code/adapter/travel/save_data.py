"""Saving data from the last.fm datasets"""

import csv
import os
import re
from datetime import datetime
from dateutil.parser import parse

from models import *



regexp_url = r'/zajezdy/zobrazit/(?P<tour_type>[\w-]+)/(?P<country_name>[\w-]+)/(?P<tour_name>[\w-]+)/*'

# relative paths to the dataset files
filename_all =  '../../datasets/travel/travel.csv'

separator = ','

decay_secs = 1200

ACTIONS = {
    'HREF_CLICK': Click,
    'ON_PAGE': MouseMove,
    'OBJECT_INTERACTION': {
        'ORDER': Order,
        'QUESTION': Question,
    },
    'PAGE_OPEN': ViewProfile,
    'PAGE_CLOSE': None,
}
"""Dictionary action: class to save"""

def save_data():
    """Save the data"""
        
    _parse_all(filename_all)
    print "All saved."
    

"""
1,3,1,2010-04-23 11:37:34,PAGE_OPEN,REF: http://slantour.cz/zajezdy/katalog/za-sportem,/
2,3,1,2010-04-23 11:37:35,PAGE_CLOSE,,/
4,3,1,2010-04-23 11:37:36,PAGE_OPEN,REF: http://slantour.cz/,/zajezdy/katalog/pobytove-zajezdy
5,3,1,2010-04-23 11:37:37,PAGE_CLOSE,,/zajezdy/katalog/pobytove-zajezdy
7,3,1,2010-04-23 11:37:38,PAGE_OPEN,REF: http://slantour.cz/zajezdy/katalog/pobytove-zajezdy,/zajezdy/katalog/pobytove-zajezdy/ceska-republika
8,3,1,2010-04-23 11:37:39,PAGE_CLOSE,,/zajezdy/katalog/pobytove-zajezdy/ceska-republika

Before removal:
>>> from travel.models import *
>>> from django.db.models import *
>>> User.objects.count()
12991
>>> Click.objects.count()
17426
>>> Question.objects.count()
21
>>> Order.objects.count()
227
>>> MouseMove.objects.count()
68759
>>> Session.objects.count()
14409
>>> Tour.objects.count()
702
>>> TourType.objects.count()
6
>>> TourType.objects.all()
[<TourType: pobytove-zajezdy>, <TourType: poznavaci-zajezdy>, <TourType: za-sportem>, <TourType: lazenske-pobyty>, <TourType: jednodenni-zajezdy>, <TourType: lyzovani>]
>>> Country.objects.count()
50
>>> User.objects.annotate(scount=Count('session')).filter(scount__gt=1).count()
834
>>> ViewProfile.objects.count()
40766

>>> User.objects.annotate(ocount=Count('session__order')).filter(ocount__gte=1).count()
193
>>> User.objects.annotate(ocount=Count('session__order')).filter(ocount__gte=1).annotate(vcount=Count('session__viewprofile')).aggregate(Avg('vcount'))
{'vcount__avg': 9.3161000000000005}
>>> User.objects.annotate(ocount=Count('session__order')).filter(ocount__gte=1).annotate(vcount=Count('session__mousemove')).aggregate(Avg('vcount'))
{'vcount__avg': 28.590699999999998}
>>> User.objects.annotate(ocount=Count('session__order')).filter(ocount__gte=1).annotate(vcount=Count('session__question')).aggregate(Sum('vcount'))
{'vcount__sum': 5}
>>> User.objects.annotate(ocount=Count('session__order')).filter(ocount__gte=1).annotate(vcount=Count('session__click')).aggregate(Avg('vcount'))
{'vcount__avg': 3.9430000000000001}

After removal:
>>> User.objects.count()
193
>>> Click.objects.count()
672
>>> Click.objects.values_list('session__user', 'tour').distinct().count()
226
>>> Question.objects.count()
5
>>> Question.objects.values_list('session__user', 'tour').distinct().count()
4
>>> Order.objects.count()
227
>>> Order.objects.values_list('session__user', 'tour').distinct().count()
194
>>> MouseMove.objects.count()
4570
>>> MouseMove.objects.values_list('session__user', 'tour').distinct().count()
551
>>> Session.objects.count()
333
>>> Tour.objects.count()
753
>>> TourType.objects.count()
6
>>> Country.objects.count()
50
>>> ViewProfile.objects.count()
1551
>>> ViewProfile.objects.values_list('session__user', 'tour').distinct().count()
619
>>> ViewProfile.objects.aggregate(Max('duration'))
{'duration__max': 1195}
>>> 1195/60
19
>>> ViewProfile.objects.aggregate(Avg('duration'))
{'duration__avg': 88.494500000000002}
>>> User.objects.annotate(hh=Count('session__click')).filter(hh=0).count()
67
>>> User.objects.annotate(hh=Count('session__mousemove')).filter(hh=0).count()
0
>>> User.objects.annotate(hh=Count('session__viewprofile')).filter(hh=0).count() 
8
>>> Tour.objects.filter(viewprofile__isnull=False).distinct().count()
288

After 0.2 division
45 test pairs selected from total 227 pairs.
>>> ViewProfile.objects.count()
1226
>>> MouseMove.objects.count()
3645
>>> Click.objects.count()
522
>>> Question.objects.count()
4


"""

def _parse_all(filename):
    """Parse the mega csv file"""
    
    filename = _get_abs_path(filename)        

    # open the csv reader
    reader = csv.reader(open(filename, "rb"), delimiter=separator, quoting=csv.QUOTE_NONE)

    # compile the pattern
    pattern = re.compile(regexp_url)
    
    # open pages 
    open_pages = {}
    
    try:
        for x, user_id, user_session_id, timestamp, action, action_parameter, object_ in reader:
            
            if reader.line_num % 5000 == 0:
                print '%s lines processed' % reader.line_num  
                
                cur_timestamp = parse(timestamp)

                # do the cleanup
                open_pages = dict((k, view_page) for (k, view_page) in open_pages.items() 
                    if (cur_timestamp - view_page.timestamp).seconds > decay_secs)
                    
            # parse the ids
            user_id = int(user_id)
            
            # take only users that bought something
            if not (user_id in USERS_IDS_ORDER):
                continue
                
            # find out whether it's done on an interesting object - tour.
            # try matching the object, if it's not, go on
            m = pattern.match(object_)
            
            if not m:
                continue

            # try getting the action class, if not available, continue
            try:
                act_class = ACTIONS[action]
            except KeyError:
                continue
            
            # for object interaction it's a bit more difficult
            if action == 'OBJECT_INTERACTION':            
                try:
                    act_class = act_class[action_parameter]
                except KeyError:
                    continue
            
                
            # prepare the user
            #

            # parse the ids
            user_session_id = int(user_session_id)
            
            # get or create the user, session
            user, x = User.objects.get_or_create(id=user_id)
            session, x = Session.objects.get_or_create(user=user, session_no=user_session_id)
            
            
            # prepare the tour
            #
            
            # get the matched stuff
            country_name = m.group('country_name')
            tour_type_name = m.group('tour_type')
            tour_name = m.group('tour_name')
            
            # get or create the country, tour type.
            country, x = Country.objects.get_or_create(name=country_name)
            tour_type, x = TourType.objects.get_or_create(name=tour_type_name)
            tour, x = Tour.objects.get_or_create(
                name=tour_name, 
                defaults={
                    'country': country,
                    'tour_type': tour_type,
                    'url': object_,
                }
            )
            
            # parse the date
            timestamp = parse(timestamp)
            
            # open/close page need special handling
            #
            
            if action == 'PAGE_OPEN':
                
                view_page = act_class(
                    session=session,
                    tour=tour,
                    timestamp=timestamp)
                
                # save the action to the dictionary waiting for the close event
                open_pages[(tour, user)] = view_page
                
                continue
            
            if action == 'PAGE_CLOSE':

                # try finding the open, if not present, go ahead
                try:
                    view_page = open_pages[(tour, user)]
                except KeyError:
                    continue
                
                # count the duration and save the event if reasonable
                view_page.duration = (timestamp - view_page.timestamp).seconds

                if view_page.duration < decay_secs:
                    view_page.save()

                continue
            
            # create the action
            act_class.objects.create(
                session=session,
                tour=tour,
                timestamp=timestamp)
    except:
        print "error on line %d" % reader.line_num
        raise

        
def _get_abs_path(filename):
    """Get the absolute path from the relative"""
    return os.path.join(os.path.dirname(__file__), filename)
    

