from django.conf.urls.defaults import *

from settings import SERVE_STATIC_FILES, MEDIA_ROOT

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    # the demo app    
    (r'^', include('demo.urls', namespace='demo'))
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
)
if SERVE_STATIC_FILES:
    urlpatterns += patterns('',
        # for working with static files (for development only)
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}) 
    )
