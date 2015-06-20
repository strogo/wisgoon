from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from feedreader.api import UserResource

admin.autodiscover()

user_resource = UserResource()

urlpatterns = patterns('',
    url(r'^$', 'pin.views.home', name='home'),
    # url(r'^latest_post/', 'latest_redis', name='pin-latest-old'),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^pin/', include('pin.urls')),
    # url(r'^feedback/', include('contactus.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # url(r'', include('social_auth.urls')),
    url(r'^acc/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^api/', include(user_resource.urls)),
    url(r'^policy/', 'pin.views.policy', name='policy'),
    url(r'^stats/', 'pin.views.stats', name='stats'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^buggy/', 'pin.views_test.buggy', name='buggy'),

)

urlpatterns += patterns('pin.views',
    url(r'^latest/$', 'latest_redis', name='pin-latest'),
    
    url(r'^rp/$', 'rp', name='rp'),

    url(r'^feedback/$', 'feedback', name='pin-feedback'),
    url(r'^last/likes/$', 'last_likes', name='pin-last-likes'),

    url(r'^category/(?P<cat_id>\d+)/$', 'category_redis', name='pin-category'),
    url(r'^category/(?P<category_id>\d+)/top/$', 'category_top', name='pin-category-top'),

    url(r'^search/', 'search', name='search'),
    url(r'^tag/(?P<tag_name>.*)/$', 'tags', name='tags'),
    url(r'^hashtag/(?P<tag_name>.*)/$', 'hashtag', name='hashtags'),

    url(r'^user/(?P<user_id>\d+)/$', 'user', name='pin-user'),
    url(r'^user/(?P<user_id>\d+)/likes/$', 'user_like', name='pin-user-like'),
    url(r'^user/(?P<user_id>\d+)/friends/$', 'user_friends', name='pin-user-friends'),
    url(r'^user/(?P<user_id>\d+)/following/$', 'user_friends', name='pin-user-following'),
    url(r'^user/(?P<user_id>\d+)/followers/$', 'user_followers', name='pin-user-followers'),

    url(r'^popular/(?P<interval>\w+)/$', 'popular', name='pin-popular-offset'),
    url(r'^popular/', 'popular', name="pin-popular"),
    url(r'^topuser/$', 'topuser', name='pin-topuser'),
    url(r'^top-group-user/$', 'topgroupuser', name='pin-topgroupuser'),
)

urlpatterns += patterns('pin.views3_api',
    url(r'^api/v3/post/latest/$', 'post_latest', name="api-3-latest"),
    url(r'^api/v3/post/item/(?P<post_id>\d+)/$', 'post_item', name="api-3-item"),
)

urlpatterns += patterns('pin.views4_api',
    url(r'^api/v4/user/blockers/$', 'user_blockers', name="api-4-blockers"),
    url(r'^api/v4/user/near_by/$', 'user_near_by', name="api-4-nearby"),
)

if not settings.DEBUG:
    urlpatterns += patterns('pin.views',
        url(r'^(?P<user_namefl>.*)/followers/$', 'absuser_followers', name='pin-absuser-followers'),
        url(r'^(?P<user_namefg>.*)/following/$', 'absuser_friends', name='pin-absuser-following'),
        url(r'^(?P<user_namel>.*)/likes/$', 'absuser_like', name='pin-absuser-like'),
        url(r'^(?P<user_name>.*)/$', 'absuser', name='pin-absuser'),
    )
