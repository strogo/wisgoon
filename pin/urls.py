from django.conf.urls import patterns, include, url
from django.contrib import admin

from pin.feeds import EditorPinFeed
from pin.api import PostResource, CategotyResource, CommentResource,\
    ProfileResource, AppResource, StreamResource

admin.autodiscover()

post_resource = PostResource()
cat_resource = CategotyResource()
comment_resource = CommentResource()

profile_resource = ProfileResource()
app_resource = AppResource()

stream_resource = StreamResource()


urlpatterns = patterns('pin.views',
    url(r'^$', 'home', name='pin-home'),
    url(r'^angular/$', 'angular', name='pin-angular-home'),
    url(r'^queue/$', 'home_queue', name='pin-home-queue'),
    url(r'^search/', 'search', name='search'),
    url(r'^(?P<item_id>\d+)/$', 'item', name="pin-item"),
    url(r'^(?P<item_id>\d+)/related/$', 'item_related', name="pin-item-related"),
    url(r'^user/(?P<user_id>\d+)/likes/$', 'user_like', name='pin-user-like'),
    url(r'^user/(?P<user_id>\d+)/friends/$', 'user_friends', name='pin-user-friends'),
    url(r'^user/(?P<user_id>\d+)/following/$', 'user_friends', name='pin-user-following'),
    url(r'^user/(?P<user_id>\d+)/followers/$', 'user_followers', name='pin-user-followers'),
    url(r'^user/(?P<user_id>\d+)/$', 'user', name='pin-user'),
    url(r'^user/(?P<user_id>\d+)/(?P<user_name>\w+)/$', 'user', name='pin-user-new'),
    url(r'^likers/(?P<post_id>\d+)/(?P<offset>\d+)/$', 'post_likers', name='pin-likers'),
    url(r'^likers/(?P<post_id>\d+)/$', 'post_likers', name='pin-likers'),

    url(r'^com/posts/(?P<post_id>\d+)/', 'get_comments', name='pin-get-comments'),
    url(r'^editor/choices/feed/', EditorPinFeed(), name="pin-latest-feed"),

    url(r'^check_user_agent/', 'check_user_agent', name='pin-get-check-user-agent'),

    url(r'^popular/(?P<interval>\w+)/$', 'popular', name='pin-popular-offset'),
    url(r'^popular/', 'popular', name="pin-popular"),
    url(r'^topuser/$', 'topuser', name='pin-topuser'),
    url(r'^top-group-user/$', 'topgroupuser', name='pin-topgroupuser'),

    url(r'^category/(?P<cat_id>\d+)', 'category', name='pin-category'),

    url(r'^api1/', include(post_resource.urls)),
    url(r'^apic/', include(cat_resource.urls)),
    url(r'^api/app/', include(app_resource.urls)),
    url(r'^api/stream/', include(stream_resource.urls)),
)

urlpatterns += patterns('pin.views_user',
    url(r'^notif/$', 'notif_user', name="pin-notif-user"),
    url(r'^following/activity/$', 'notif_following', name="pin-notif-user-following"),
    url(r'^notif/all/$', 'notif_all', name="pin-notif-user-all"),
    url(r'^like/(?P<item_id>\d+)', 'like', name="pin-item-like"),
    url(r'^following/$', 'following', name='pin-following'),
    url(r'^follow/$', 'follow', name='pin-follow'),
    url(r'^follow/(?P<following>\d+)/(?P<action>\d+)/$', 'follow', name='pin-follow'),
    url(r'^send_comment/', 'send_comment', name='pin-comment'),
    url(r'^comment/score/(?P<comment_id>\d+)/(?P<score>\d+)', 'comment_score', name="pin-comment-score"),
    url(r'^show_notify/', 'show_notify', name="show_notify"),
    url(r'^you_are_deactive', 'you_are_deactive', name='pin-you-are-deactive'),
    url(r'^report/(?P<pin_id>\d+)', 'report', name='report_pin'),
    url(r'^delete/(?P<item_id>\d+)', 'delete', name="pin-item-delete"),
    url(r'^nop/(?P<item_id>\d+)', 'nop', name="pin-item-nop"),
    url(r'^ajax_upload/$', 'upload', name="pin-upload"),
    url(r'^ajax_url/$', 'a_sendurl', name="pin-sendurl-a"),
    url(r'^edit/(?P<post_id>\d+)/$', 'edit', name="pin-item-edit"),
    url(r'^sendurl/$', 'sendurl', name="pin-sendurl"),
    url(r'^send/$', 'send', name="pin-send"),
    url(r'^inc/credit/$', 'inc_credit', name="pin-inc-credit"),
    url(r'^verify_payment/(?P<bill_id>\w+)/$', 'verify_payment', name="pin-verify-payment"),
    url(r'^save/as/ads/(?P<post_id>\w+)/$', 'save_as_ads', name="pin-save-as-ads"),
    url(r'^user/action/(?P<user_id>\d+)/$', 'block_action', name="pin-user-block"),
    url(r'^blocked/$', 'blocked_list', name="blocked-list"),
    url(r'^promotion/$', 'promotion_list', name="promotion-list"),
)

# urlpatterns += patterns('pin.views_backbone',
#     url(r'new/home', 'home', name='new-home'),
#     url(r'new/notif/', 'notif', name='new-notif'),
# )

urlpatterns += patterns('pin.views_oauth',
    url(r'invite/google', 'invite_google', name='invite-google'),
    url(r'email/activation/$', 'activation_email', name='activation_email'),
)

# urlpatterns += patterns('pin.views_static',
#     url(r'app/android/', 'android', name='static-android'),
# )

urlpatterns += patterns('pin.views_admin',
    url(r'user/activate/(?P<user_id>\d+)/(?P<status>\d+)/$', 'activate_user', name='activate-user'),
    url(r'^goto_index/(?P<item_id>\d+)/(?P<status>\d+)/', 'goto_index', name='pin-item-goto-index'),

    url(r'^comment/delete/(?P<id>\d+)', 'comment_delete', name="pin-comment-delete"),
)

urlpatterns += patterns('',
    url(r'^api/post/(?P<item_id>\d+)/$', 'pin.views2_api.post_item', name="post_api_item"),
    url(r'^api/post/(?P<post_id>\d+)/details/', 'pin.views2_api.post_details', name="post_api_details"),
    url(r'^api/post/', 'pin.views2_api.post', name="post_api"),
    url(r'^api/notif/notify/$', 'pin.views2_api.notif', name="new_notif"),
    url(r'^api/notif/count/$', 'pin.views2_api.notif_count', name="new_notif_count"),
    url(r'^api/system/$', 'pin.views2_api.system', name="api-system"),

    url(r'^api/packages/$', 'pin.views2_api.packages_old', name="api-packages_old"),
    url(r'^api/packages2/$', 'pin.views2_api.packages', name="api-packages"),

    url(r'^api/logout/$', 'pin.views2_api.logout', name="api-logout"),
)
