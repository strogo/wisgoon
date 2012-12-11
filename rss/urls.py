from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('rss.views',
    # Examples:
    url(r'^$', 'home', name='rss'),
    url(r'^subscribe/$', 'subscribe', name="rss-subs"),
    url(r'^subscribe_m/$', 'subscribe_modal', name="rss-subs-modal"),
    url(r'^feed/(?P<feed_id>\d+)/$', 'feed', name="rss-feed"),
    url(r'^feed/(?P<feed_id>\d+)/(?P<item_id>\d+)/$', 'feed_item', name="rss-item"),
    url(r'^feed/item/(?P<item_id>\d+)/goto$', 'feed_item_goto', name="rss-item-goto"),
    url(r'^feed/like/(?P<item_id>\d+)', 'like', name="rss-item-like"),
    url(r'^lastview/', 'lastview', name="rss-lastview"),
    url(r'^feed/sub/(?P<feed_id>\d+)', 'a_sub', name="rss-feed-sub"),
    url(r'^search', 'search', name="rss-search"),
    url(r'^comments/posted/$', 'comment_posted'),
    url(r'^report/$', 'report', name="rss-item-report"),
    url(r'^user/likes/(?P<user_id>\d+)', 'user_likes', name="rss-item-likes"),
    
)

urlpatterns += patterns('', 
    url(r'^comments/', include('django.contrib.comments.urls')),
)
