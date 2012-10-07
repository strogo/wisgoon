from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('rss.views',
    # Examples:
    url(r'^$', 'home', name='rss'),
    url(r'^subscribe/$', 'subscribe', name="rss-subs"),
    url(r'^feed/(?P<feed_id>\d+)/$', 'feed', name="rss-feed"),
    url(r'^feed/(?P<feed_id>\d+)/(?P<item_id>\d+)/$', 'feed_item', name="rss-item"),
    url(r'^feed/item/(?P<item_id>\d+)/goto$', 'feed_item_goto', name="rss-item-goto"),
    url(r'^feed/like/(?P<item_id>\d+)', 'like', name="rss-item-like"),
    url(r'^feed/sub/(?P<feed_id>\d+)', 'a_sub', name="rss-feed-sub"),
    url(r'^search', 'search', name="rss-search"),
    url(r'^comments/posted/$', 'comment_posted'),
    url(r'^feed/report/(?P<item_id>\d+)', 'report', name="rss-item-report"),
    
)
urlpatterns += patterns('', 
    url(r'^comments/', include('django.contrib.comments.urls')),
)
