from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.dashboard.api.home',
                       url(r'home/', 'dashboard_home', name='dashboard-api-home'),
                       )

urlpatterns += patterns('pin.views2.dashboard.api.monthly_chart',
                        url(r'bill_stats/', 'bill_stats',
                            name='dashboard-api-bill-stats'),
                        url(r'follow_stats/', 'follow_stats',
                            name='dashboard-api-follow-stats'),
                        url(r'comment_stats/', 'comment_stats',
                            name='dashboard-api-comment-stats'),
                        url(r'like_stats/', 'like_stats',
                            name='dashboard-api-like-stats'),
                        url(r'block_stats/', 'block_stats',
                            name='dashboard-api-block-stats'),
                        )

urlpatterns += patterns('pin.views2.dashboard.api.post',
                        url(r'post/reported/', 'reported',
                            name='dashboard-api-post-reported'),
                        url(r'post/enableAds/', 'enable_ads',
                            name='dashboard-api-post-ads-enable'),
                        url(r'post/disableAds/', 'disable_ads',
                            name='dashboard-api-post-ads-disable'),
                        url(r'post/category/chart/', 'post_of_category',
                            name='dashboard-api-post-category'),
                        url(r'post/showAds/', 'show_ads',
                            name='dashboard-api-post-ads-show'),
                        url(r'post/delete/', 'delete_post',
                            name='dashboard-api-post-delete'),
                        url(r'post/report/undo/', 'post_undo',
                            name='dashboard-api-post-undo_report'),
                        )


urlpatterns += patterns('pin.views2.dashboard.api.log',
                        url(r'log/show/', 'show_log',
                            name='dashboard-api-log-show'),
                        )

urlpatterns += patterns('pin.views2.dashboard.api.user',
                        url(r'user/search/', 'search_user',
                            name='dashboard-api-user-search'),
                        )
