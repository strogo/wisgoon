import os
from django.conf.urls import patterns, include, url
from django.contrib import admin

from feedreader.settings import SITE_ROOT
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rss.views.home', name='home'),
    url(r'^feedreader/', include('rss.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('', 
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
        {'document_root': os.path.join(SITE_ROOT, 'media')})
)