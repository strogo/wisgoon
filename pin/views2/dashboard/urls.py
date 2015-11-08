from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.dashboard.home',
                       url(r'^$', 'home', name='dashboard-home'),
)

urlpatterns += patterns('pin.views2.dashboard.post',
                       url(r'^posts/$', 'home', name='dashboard-post-home'),
                       url(r'^post/reported/$', 'reported', name='dashboard-post-reported'),
)
