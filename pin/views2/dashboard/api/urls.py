from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.dashboard.api.home',
                       url(r'home/', 'dashboard_home', name='dashboard-api-home'),
                       )

urlpatterns += patterns('pin.views2.dashboard.api.monthly_chart',
                        url(r'bill_stats/', 'bill_stats', name='dashboard-api-bill-stats'),
                        url(r'follow_stats/', 'follow_stats', name='dashboard-api-follow-stats'),
                        url(r'comment_stats/', 'comment_stats', name='dashboard-api-comment-stats'),
                        url(r'like_stats/', 'like_stats', name='dashboard-api-like-stats'),
                        url(r'block_stats/', 'block_stats', name='dashboard-api-block-stats'),
                        )

urlpatterns += patterns('pin.views2.dashboard.api.post',
                        url(r'post/reported/', 'reported', name='dashboard-api-post-reported'),
                        )
