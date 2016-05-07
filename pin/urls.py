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

    url(r'^popular/(?P<interval>\w+)/$', 'popular', name='pin-popular-offset'),
    url(r'^popular/', 'popular', name="pin-popular"),
    url(r'^topuser/$', 'topuser', name='pin-topuser'),
    url(r'^top-group-user/$', 'topgroupuser', name='pin-topgroupuser'),

    url(r'^category/(?P<cat_id>\d+)', 'category', name='pin-category'),

    url(r'^api1/', include(post_resource.urls)),
    url(r'^apic/', include(cat_resource.urls)),
    url(r'^api/profile/', include(profile_resource.urls)),
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

urlpatterns += patterns('pin.views_backbone',
    url(r'new/home', 'home', name='new-home'),
    url(r'new/notif/', 'notif', name='new-notif'),
)

urlpatterns += patterns('pin.views_oauth',
    url(r'invite/google', 'invite_google', name='invite-google'),
    url(r'email/activation/$', 'activation_email', name='activation_email'),
)

urlpatterns += patterns('pin.views_static',
    url(r'app/android/', 'android', name='static-android'),
)

urlpatterns += patterns('pin.views_admin',
    url(r'user/activate/(?P<user_id>\d+)/(?P<status>\d+)/$', 'activate_user', name='activate-user'),
    url(r'^goto_index/(?P<item_id>\d+)/(?P<status>\d+)/', 'goto_index', name='pin-item-goto-index'),

    url(r'^comment/delete/(?P<id>\d+)', 'comment_delete', name="pin-comment-delete"),
)

urlpatterns += patterns('pin.views_device',
    url(r'^d_send/$', 'post_send', name="pin-direct"),
    url(r'^d_like/$', 'like', name='pin-device-like'),
    url(r'^d_post_comment/$', 'post_comment', name='pin-device-post-comment'),
    url(r'^d_post_report/$', 'post_report'),
    url(r'^d/comment/score/(?P<comment_id>\d+)/(?P<score>\d+)/$', 'comment_score'),
    url(r'^d/post/delete/(?P<item_id>\d+)/$', 'post_delete'),
    url(r'^d/post/update/(?P<item_id>\d+)/$', 'post_update'),
    url(r'^d/comment/report/(?P<comment_id>\d+)/$', 'comment_report'),
    url(r'^d/follow/(?P<following>\d+)/(?P<action>\d+)/$', 'follow'),

)

urlpatterns += patterns('',
    url(r'^api/post/(?P<item_id>\d+)/$', 'pin.views2_api.post_item', name="post_api_item"),
    url(r'^api/post/(?P<post_id>\d+)/details/', 'pin.views2_api.post_details', name="post_api_details"),
    url(r'^api/post_back/', 'pin.views2_api.post', name="post_api_back"),
    url(r'^api/post/', 'pin.views2_api.post2', name="post_api"),
    url(r'^api/promoted/post/', 'pin.views2_api.promoted', name="promoted_api"),
    url(r'^api/hashtag/$', 'pin.views2_api.hashtag', name="api-hashtag"),
    url(r'^api/hashtag/top/$', 'pin.views2_api.hashtag_top', name="api-hashtag-top"),
    url(r'^api/com/comments/', 'pin.views2_api.comments', name="api_comments"),
    url(r'^api/friends_post/', 'pin.views2_api.friends_post', name="post_friends_api"),
    url(r'^api/like/likes/', 'pin.views2_api.likes', name="likes_api"),
    url(r'^api/notif/notify/$', 'pin.views2_api.notif', name="new_notif"),
    url(r'^api/notif/count/$', 'pin.views2_api.notif_count', name="new_notif_count"),
    url(r'^api/comment/delete/(?P<id>\d+)/$', 'pin.views2_api.comment_delete', name="new_comment_delete"),

    url(r'^api/following/(?P<user_id>\d+)/', 'pin.views2_api.following', name="api-following"),
    url(r'^api/follower/(?P<user_id>\d+)/', 'pin.views2_api.follower', name="api-follower"),
    url(r'^api/search/$', 'pin.views2_api.search', name="api-search"),
    url(r'^api/v2/search/$', 'pin.views2_api.search2', name="api-search-v2"),

    url(r'^api/search/posts/$', 'pin.views2_api.search_posts', name="api-search-posts"),
    url(r'^api/system/$', 'pin.views2_api.system', name="api-system"),

    url(r'^api/block/user/(?P<user_id>\d+)/', 'pin.views2_api.block_user', name="api-block"),
    url(r'^api/unblock/user/(?P<user_id>\d+)/', 'pin.views2_api.unblock_user', name="api-block"),

    url(r'^api/packages/$', 'pin.views2_api.packages_old', name="api-packages_old"),
    url(r'^api/packages2/$', 'pin.views2_api.packages', name="api-packages"),

    url(r'^api/promotion/prices/$', 'pin.views2_api.promotion_prices', name="api-promotion-prices"),
    url(r'^api/user/credit/$', 'pin.views2_api.user_credit', name="api-user-credit"),
    url(r'^api/user/inc/credit/$', 'pin.views2_api.inc_credit', name="api-user-inc-credit"),

    url(r'^api/save/as/ads/(?P<post_id>\d+)/$', 'pin.views2_api.save_as_ads', name="api-save-as-ads"),

    url(r'^api/gcm/get/phone/data/$', 'pin.views2_api.get_phone_data', name="api-get-phone-data"),
    url(r'^api/plus/get/data/$', 'pin.views2_api.get_plus_data', name="api-get-phone-data"),
    url(r'^api/logout/$', 'pin.views2_api.logout', name="api-logout"),

    url(r'^api/password/reset_mobile/$', 'pin.views2_api.password_reset',
        name='api_password_reset'),

    url(r'^api/password/change_mobile/$', 'pin.views2_api.change_password',
        name='password_change_mobile'),
)
