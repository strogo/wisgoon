from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('rss.views',
    # Examples:
    url(r'^$', 'home', name='home'),
    url(r'^subscribe/$', 'subscribe', name="rss-subs"),
    url(r'^feed/(?P<feed_id>\d+)/$', 'feed', name="rss-feed"),
    #url(r'^', include('rss.urls')),
)
