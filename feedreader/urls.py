from django.conf.urls import patterns, include, url
from django.contrib import admin
from feedreader.api import UserResource

admin.autodiscover()

user_resource = UserResource()

urlpatterns = patterns('',
    url(r'^$', 'pin.views.home', name='home'),
    # url(r'^latest_post/', 'latest_redis', name='pin-latest-old'),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^pin/', include('pin.urls')),
    url(r'^feedback/', include('contactus.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^acc/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^api/', include(user_resource.urls)),
    url(r'^policy/', 'pin.views.policy', name='policy'),
    url(r'^stats/', 'pin.views.stats', name='stats'),
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += patterns('pin.views',
    url(r'^latest/$', 'latest_redis', name='pin-latest'),
    url(r'^last/likes/$', 'last_likes', name='pin-last-likes'),

    url(r'^category/(?P<cat_id>\d+)', 'category_redis', name='pin-category'),

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
    
)
