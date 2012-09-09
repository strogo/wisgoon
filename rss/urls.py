from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('rss.views',
    # Examples:
    url(r'^$', 'home', name='home'),
    url(r'^subscribe/$', 'subscribe', name="rss-subs"),
    url(r'^feed/(?P<feed_id>\d+)/$', 'feed', name="rss-feed"),
    url(r'^feed/(?P<feed_id>\d+)/(?P<item_id>\d+)/$', 'feed_item', name="rss-item"),
    #url(r'^', include('rss.urls')),
)
