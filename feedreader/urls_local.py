import os

from feedreader.settings import SITE_ROOT

from urls import *

urlpatterns += patterns('', 
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
        {'document_root': os.path.join(SITE_ROOT, 'media')})
)

urlpatterns += patterns('pin.views',
    url(r'^(?P<user_namefl>.*)/followers/$', 'absuser_followers', name='pin-absuser-followers'),
    url(r'^(?P<user_namefg>.*)/following/$', 'absuser_friends', name='pin-absuser-following'),
    url(r'^(?P<user_namel>.*)/likes/$', 'absuser_like', name='pin-absuser-like'),
    url(r'^(?P<user_name>.*)/$', 'absuser', name='abspin-user'),
    # url(r'^(?P<user_namef>.*)/friends/$', 'user_friends', name='pin-user-friends'),
)
