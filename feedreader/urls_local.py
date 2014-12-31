import os

from feedreader.settings import SITE_ROOT

from urls import *

urlpatterns += patterns('', 
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
        {'document_root': os.path.join(SITE_ROOT, 'media')})
)
