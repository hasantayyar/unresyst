"""Urls for the demo application"""

from django.conf.urls.defaults import *

urlpatterns = patterns('demo.views',
                       
    # shoe recommendations
    url(regex=r'^user/(?P<user_name>[\w-]+)/shoe-recommendations/$',
        view='view_recommendations', 
        name="recommendations"
    ),

    # home page
    url(regex=r'^$',
        view='view_home_page',
        name='home_page'
    )      
)    
