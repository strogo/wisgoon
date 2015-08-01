from django.conf.urls import patterns, url

urlpatterns = patterns('pin.api5.auth',
                       url(r'auth/register/$', 'register', name='api-5-auth-register'),
                       url(r'auth/login/$', 'login', name='api-5-auth-login'),
                       url(r'auth/follow/$', 'follow', name='api-5-auth-follow'),
                       url(r'auth/unfollow/$', 'unfollow', name='api-5-auth-unfollow'),
                       url(r'auth/followers/(?P<user_id>\d+)/$', 'followers', name='api-5-auth-followers'),
                       url(r'auth/following/(?P<user_id>\d+)/$', 'following', name='api-5-auth-following'),
)

urlpatterns += patterns('pin.api5.post',
                       url(r'post/latest/$', 'latest', name='api-5-post-latest'),
                       url(r'post/choices/$', 'choices', name='api-5-post-choices'),
                       url(r'post/friends/$', 'friends', name='api-5-post-friends'),
                       url(r'post/category/(?P<category_id>\d+)/$', 'category', name='api-5-post-category'),
                       url(r'post/item/(?P<item_id>\d+)/$', 'item', name='api-5-post-item'),
)
