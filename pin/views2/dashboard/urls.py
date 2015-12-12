from django.conf.urls import patterns, url, include

urlpatterns = patterns('pin.views2.dashboard.home',
                       url(r'^$', 'home', name='dashboard-home'),
                       url(r'^api/$', include('pin.views2.dashboard.api.urls')),
                       )

urlpatterns += patterns('pin.views2.dashboard.post',
                        url(r'^posts/$', 'home', name='dashboard-post-home'),
                        url(r'^post/reported/$', 'reported', name='dashboard-post-reported'),
                        url(r'^post/user_activity/$', 'user_activity', name='dashboard-user-activity'),
                        url(r'^post/logs/$', 'logs', name='dashboard-logs'),
                        url(r'^post/ads/$', 'ads', name='dashboard-ads'),
                        url(r'^post/catregory/$', 'catregory', name='dashboard-catregory'),


                        )
