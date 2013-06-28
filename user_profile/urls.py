from django.conf.urls import patterns, include, url

urlpatterns = patterns('user_profile.views',
    # Examples:
    url(r'^change/$', 'change', name="user-profile-change"),
    url(r'^d_change/$', 'd_change', name="device-user-profile-change"),
)

