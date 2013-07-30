from django.conf.urls import patterns, include, url
from django.contrib import admin

from pin.feeds import LatestPinFeed
from pin.api import PostResource, CategotyResource, CommentResource, NotifyResource, ProfileResource

admin.autodiscover()

post_resource=PostResource()
cat_resource=CategotyResource()
comment_resource = CommentResource()
notify_resource = NotifyResource()
profile_resource = ProfileResource()

urlpatterns = patterns('pin.views',
    url(r'^$', 'home', name='pin-home'),
    url(r'^latest_post/', 'latest', name='pin-latest'),
    url(r'^(?P<item_id>\d+)/$', 'item', name="pin-item"),
    url(r'^send/$', 'send', name="pin-send"),
    url(r'^d_send/$', 'd_send', name="pin-direct"),
    
    
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
    url(r'^tag/(.*)/', 'tag', name="pin-tag"),
    url(r'^show_notify/', 'show_notify', name="show_notify"),
    url(r'^latest/feed/', LatestPinFeed(), name="pin-latest-feed"),
    url(r'^popular/(?P<interval>\w+)/$', 'popular', name='pin-popular-offset'),
    url(r'^popular/', 'popular', name="pin-popular"),
    url(r'^topuser/$', 'topuser', name='pin-topuser'),
    url(r'^top-group-user/$', 'topgroupuser', name='pin-topgroupuser'),
    url(r'^notif/$','notif_user', name="pin-notif-user"),
    url(r'^report/(?P<pin_id>\d+)','report',name='report_pin'),

    url(r'^trust/user/(?P<user_id>\d+)','trust_user',name='trust_user'),
    url(r'^send_comment/', 'send_comment', name='pin-comment'),
    url(r'^comment/delete/(?P<id>\d+)', 'comment_delete', name="pin-comment-delete"),
    url(r'^comment/approve/(?P<id>\d+)', 'comment_approve', name="pin-comment-approve"),
    url(r'^comment/unapprove/(?P<id>\d+)', 'comment_unapprove', name="pin-comment-unapprove"),
    #url(r'^mylike/', 'mylike', name='pin-mylike'),
    url(r'^you_are_deactive', 'you_are_deactive', name='pin-you-are-deactive'),
    url(r'^goto_index/(?P<item_id>\d+)/(?P<status>\d+)/', 'goto_index', name='pin-item-goto-index'),
    url(r'^send_mail', 'send_mail', name='pin-sendmail'),

    #url(r'^test_page', 'test_page', name='google_contacts_login'),

    url(r'^category/(?P<cat_id>\d+)', 'category', name='pin-category'),
    #url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    #not stables
    url(r'^delneveshte/', 'delneveshte', name="pin-delneveshte"),
    url(r'^api/', include(post_resource.urls)),
    url(r'^apic/',include(cat_resource.urls)),
    url(r'^api/com/', include(comment_resource.urls)),
    url(r'^api/notif/', include(notify_resource.urls)),
    url(r'^api/profile/', include(profile_resource.urls)),
)

urlpatterns += patterns('pin.views_oauth',
    url(r'invite/google', 'invite_google', name='invite-google'),
)

urlpatterns += patterns('pin.views_device',
    url(r'^d_like/$', 'like', name='pin-device-like'),
    url(r'^d_post_comment/$', 'post_comment', name='pin-device-post-comment'),
)

urlpatterns += patterns('', 
    url(r'^comments/', include('django.contrib.comments.urls')),
)
