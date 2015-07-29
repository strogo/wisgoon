from django.conf.urls import patterns, url

urlpatterns = patterns('pin.api5.auth',
                       url(r'auth/register/$', 'register', name='api-5-auth-register'),
                       url(r'auth/login/$', 'login', name='api-5-auth-login'),
                       url(r'auth/follow/$', 'follow', name='api-5-auth-follow'),
                       url(r'auth/unfollow/$', 'unfollow', name='api-5-auth-unfollow'),
                       url(r'auth/followers/(?P<user_id>\d+)/$', 'followers', name='api-5-auth-followers'),
                       url(r'auth/following/(?P<user_id>\d+)/$', 'following', name='api-5-auth-following'),
)
