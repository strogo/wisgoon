from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pin.views',
    url(r'^$', 'home', name='pin-home'),
    url(r'^(?P<item_id>\d+)/$', 'item', name="pin-item"),
    url(r'^send/$', 'send', name="pin-send"),
    url(r'^sendurl/$', 'sendurl', name="pin-sendurl"),
    url(r'^edit/(?P<post_id>\d+)/$', 'edit', name="pin-item-edit"),
    url(r'^ajax_url/$', 'a_sendurl', name="pin-sendurl-a"),
    url(r'^ajax_upload/$', 'upload', name="pin-upload" ),
    url(r'^comments/posted/$', 'comment_posted'),
    url(r'^user/(?P<user_id>\d+)/$', 'user', name='pin-user'),
    url(r'^follow/(?P<following>\d+)/(?P<action>\d+)$', 'follow', name='pin-follow'),
    url(r'^following/$','following', name='pin-following'),
    url(r'^like/(?P<item_id>\d+)', 'like', name="pin-item-like"),
    url(r'^delete/(?P<item_id>\d+)', 'delete', name="pin-item-delete"),
    url(r'^tag/complete/', 'tag_complete', name="pin-tag-complete"),
)


urlpatterns += patterns('', 
    url(r'^comments/', include('django.contrib.comments.urls')),
)
