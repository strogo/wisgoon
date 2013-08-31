from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from rss.feeds import LatestItemFeed, FeedsListFeed
admin.autodiscover()

urlpatterns = patterns('rss.views',
    # Examples:
    url(r'^$', 'home', name='rss'),
    url(r'^subscribe/$', 'subscribe', name="rss-subs"),
    url(r'^subscribe_m/$', 'subscribe_modal', name="rss-subs-modal"),
    url(r'^(?P<feed_id>\d+)/$', 'feed', name="rss-feed"),
    url(r'^(?P<feed_id>\d+)/o/(?P<older>\d+)$', 'feed', name="rss-feed-older"),
    url(r'^(?P<feed_id>\d+)/(?P<item_id>\d+)/$', 'feed_item', name="rss-item"),
    url(r'^(?P<feed_id>\d+)/(?P<item_id>\d+)/preview/$', 'feed_item_preview', name="rss-item-preview"),
    url(r'^item/(?P<item_id>\d+)/goto$', 'feed_item_goto', name="rss-item-goto"),
    url(r'^like/(?P<item_id>\d+)', 'like', name="rss-item-like"),
    url(r'^lastview/', 'lastview', name="rss-lastview"),
    url(r'^sub/(?P<feed_id>\d+)', 'a_sub', name="rss-feed-sub"),
    url(r'^search', 'search', name="rss-search"),
    url(r'^comments/posted/$', 'comment_posted'),
    url(r'^report/$', 'report', name="rss-item-report"),
    url(r'^user/likes/(?P<user_id>\d+)', 'user_likes', name="rss-item-likes"),
    url(r'^latest/feed/', LatestItemFeed(), name="rss-item-latest-feed"),
    url(r'^feeds/feed/', FeedsListFeed(), name="rss-list-feed"),
    url(r'xhr/older/', 'older', name='rss-older'),
    url(r'category/', 'category', name="rss-category"),
)

urlpatterns += patterns('', 
    url(r'^comments/', include('django.contrib.comments.urls')),
)
