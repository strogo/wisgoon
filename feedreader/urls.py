import os
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'pin.views.home', name='home'),
    url(r'^feedreader/', include('rss.urls')),
    url(r'^pin/', include('pin.urls')),
    url(r'^feedback/', include('contactus.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^acc/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^socialacc/', include('socialacc.urls')),
    url(r'^tag/(.*)/', 'rss.views.tag', name="tag"),
)
