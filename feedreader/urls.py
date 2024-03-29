from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from feedreader.api import UserResource

admin.autodiscover()

user_resource = UserResource()

urlpatterns = patterns('',
    url(r'^email/register/', 'pin.views.email_register', name='email_register'),
    url(r'^pass/reset/', 'pin.views.pass_reset', name='pass_reset'),
    url(r'^newsletter/', 'pin.views.newsletter', name='newsletter'),
    url(r'^notification/$', 'pin.views_user.user_notif', name="user-notif"),

    url(r'^$', 'pin.views.home', name='home'),
    # url(r'^latest_post/', 'latest_redis', name='pin-latest-old'),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^pin/', include('pin.urls')),
    # url(r'^feedback/', include('contactus.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    # url(r'', include('social_auth.urls')),
    # url(r'^acc/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^api/', include(user_resource.urls)),
    url(r'^policy/', 'pin.views.policy', name='policy'),
    url(r'^policy_for_mobile/', 'pin.views.policy_for_mobile', name='policy_for_mobile'),
    url(r'^about_us/', 'pin.views.about_us', name='about_us'),
    url(r'^about_us_for_mobile/', 'pin.views.about_us_for_mobile', name='about_us_for_mobile'),
    url(r'^stats/', 'pin.views.stats', name='stats'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^buggy/', 'pin.views_test.buggy', name='buggy'),
    url(r'^api/v6/', include('pin.api6.urls')),
    url(r'^dashboard/', include('pin.views2.dashboard.urls')),
    url(r'^angular/', include('pin.views2.angular.urls')),
    url(r'^shop/', include('shop.urls')),
)

urlpatterns += patterns('pin.views',
    url(r'^latest/$', 'latest', name='pin-latest'),
    url(r'^page/(?P<label>.*)/$', 'result', name='pin-result'),
    url(r'^feedback/$', 'feedback', name='pin-feedback'),

    url(r'^category/(?P<cat_id>\d+)/$', 'category', name='pin-category'),
    url(r'^category/(?P<category_id>\d+)/top/$', 'category_top', name='pin-category-top'),

    url(r'^search/', 'search', name='search'),
    url(r'^tag/(?P<tag_name>.*)/$', 'tags', name='tags'),
    url(r'^hashtag/(?P<tag_name>.*)/$', 'hashtag', name='hashtags'),

    url(r'^user/(?P<user_id>\d+)/$', 'user', name='pin-user'),
    url(r'^user/(?P<user_id>\d+)/likes/$', 'user_like', name='pin-user-like'),
    url(r'^user/(?P<user_id>\d+)/friends/$', 'user_friends', name='pin-user-friends'),
    url(r'^user/(?P<user_id>\d+)/following/$', 'user_friends', name='pin-user-following'),
    url(r'^user/(?P<user_id>\d+)/followers/$', 'user_followers', name='pin-user-followers'),

    url(r'^popular/(?P<interval>\w+)/$', 'popular_2',
        name='pin-popular-offset'),
    # url(r'^popular/(?P<interval>\w+)/$', 'popular', name='pin-popular-offset'),
    # url(r'^popular/new/(?P<interval>\w+)/$', 'popular_2', name='pin-popular-2-offset'),
    url(r'^popular/', 'popular_2', name="pin-popular"),
    url(r'^top/user/all/$', 'topuser', name='pin-topuser'),
    url(r'^top/user/monthly/$', 'leaderboard', name='pin-topmonthgroup'),
    url(r'^top/user/groups/$', 'topgroupuser', name='pin-topgroupuser'),
)

urlpatterns += patterns('pin.views3_api',
    url(r'^api/v3/post/latest/$', 'post_latest', name="api-3-latest"),
    url(r'^api/v3/post/item/(?P<post_id>\d+)/$', 'post_item', name="api-3-item"),
)

urlpatterns += patterns('pin.views4_api',
    url(r'^api/v4/user/blockers/$', 'user_blockers', name="api-4-blockers"),
    url(r'^api/v4/user/blocked/$', 'user_blocked', name="api-4-blocked"),
    url(r'^api/v4/user/near_by/$', 'user_near_by', name="api-4-nearby"),
    url(r'^api/v4/user/register/$', 'register', name="api-4-register"),
    url(r'^api/v4/user/block/$', 'block_user', name="api-4-block"),
    url(r'^api/v4/user/unblock/$', 'unblock_user', name="api-4-unblock"),
    url(r'^api/v4/user/follow/$', 'follow', name="api-4-follow"),
    url(r'^api/v4/user/unfollow/$', 'unfollow', name="api-4-unfollow"),
    url(r'^api/v4/user/credit/$', 'user_credit', name="api-4-user-credit"),
    url(r'^api/v4/user/check/username/$', 'user_check_username', name="api-4-user-check-username"),

)

if not settings.DEBUG:
    urlpatterns += patterns('pin.views',
        url(r'^(?P<user_namefl>.*)/followers/$', 'absuser_followers', name='pin-absuser-followers'),
        url(r'^(?P<user_namefg>.*)/following/$', 'absuser_following', name='pin-absuser-following'),
        url(r'^(?P<user_namel>.*)/likes/$', 'absuser_like', name='pin-absuser-like'),
        url(r'^(?P<user_name>.*)/$', 'absuser', name='pin-absuser'),
    )
