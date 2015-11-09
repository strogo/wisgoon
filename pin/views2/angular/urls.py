from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.angular.post',
    url(r'^$', 'home', name='angular-home'),
    url(r'^latest/$', 'latest', name='angular-post-latest'),
)
