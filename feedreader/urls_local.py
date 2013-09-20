import os
from django.conf.urls import patterns, include, url
from django.contrib import admin

from api import UserResource

from feedreader.settings import SITE_ROOT
admin.autodiscover()

user_resource = UserResource()

urlpatterns = patterns('',
    url(r'^$', 'pin.views.home', name='home'),
    url(r'^feedreader/', include('rss.urls')),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^pin/', include('pin.urls')),
    url(r'^feedback/', include('contactus.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^acc/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    #url(r'^socialacc/', include('socialacc.urls')),
    url(r'^tag/(.*)/', 'rss.views.tag', name="tag"),
    #url(r'^elections/', include('elections.urls')),
    url(r'^api/', include(user_resource.urls)),
    url(r'^policy/', 'pin.views.policy', name='policy'),
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += patterns('', 
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
        {'document_root': os.path.join(SITE_ROOT, 'media')})
)
