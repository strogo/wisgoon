from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.dashboard.api.home',
                       url(r'home/', 'dashboard_home',
                           name='dashboard-api-home'),
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

                        url(r'ads_stats/', 'ads_stats',
                            name='dashboard-api-ads-stats'),

                        url(r'user_stats/', 'join_user_state',
                            name='dashboard-api-user-stats'),
                        )

urlpatterns += patterns('pin.views2.dashboard.api.post',
                        # url(r'post/reported/', 'reported',
                        #     name='dashboard-api-post-reported'),

                        url(r'post/enableAds/', 'enable_ads',
                            name='dashboard-api-post-ads-enable'),

                        url(r'post/disableAds/', 'disable_ads',
                            name='dashboard-api-post-ads-disable'),

                        url(r'post/subcategory/chart/', 'post_of_sub_category',
                            name='dashboard-api-post-subcategory'),

                        url(r'post/category/chart/(?P<cat_name>.+\w)',
                            'post_of_category',
                            name='dashboard-api-post-category'),

                        url(r'post/showAds/', 'show_ads',
                            name='dashboard-api-post-ads-show'),

                        url(r'post/delete/', 'delete_post',
                            name='dashboard-api-post-delete'),

                        url(r'post/report/undo/', 'post_undo',
                            name='dashboard-api-post-undo_report'),

                        url(r'post/reporters/(?P<post_id>\d+)/',
                            'post_reporter_user',
                            name='dashboard-api-post-reporters'),

                        url(r'post/user/(?P<user_id>\d+)', 'post_user_details',
                            name='dashboard-api-post-user'),

                        url(r'^posts/new/report/$', 'new_report',
                            name='dashboard-api-post-new_report'),

                        url(r'^posts/undo/report/new/$', 'post_undo_new',
                            name='dashboard-api-post-post_undo_new'),

                        url(r'^delete/post/new/$', 'delete_post_new',
                            name='dashboard-api-post-delete_post_new'),

                        url(r'^post/item/new/(?P<post_id>\d+)/$', 'post_item',
                            name='dashboard-api-post-post_item'),


                        )


urlpatterns += patterns('pin.views2.dashboard.api.log',
                        url(r'log/show/', 'show_log',
                            name='dashboard-api-log-show'),

                        url(r'log/search/', 'search_log',
                            name='dashboard-api-log-search'),

                        )

urlpatterns += patterns('pin.views2.dashboard.api.user',
                        url(r'user/search/', 'search_user',
                            name='dashboard-api-user-search'),

                        url(r'user/changeStatus/', 'change_status_user',
                            name='dashboard-api-user-changeStatus'),

                        url(r'user/bannedProfile/', 'banned_profile',
                            name='dashboard-api-user-bannedProfile'),

                        url(r'user/bannedImei/', 'banned_imei',
                            name='dashboard-api-user-bannedImei'),

                        url(r'user/details/(?P<user_id>\d+)', 'user_details',
                            name='dashboard-api-user-details'),

                        url(r'user/imei/(?P<imei>\w+)', 'get_user_with_imei',
                            name='dashboard-api-user-imei'),

                        url(r'user/removeAvatar/(?P<user_id>\d+)', 'delete_user_avatar',
                            name='dashboard-api-user-remove-avatar'),

                        url(r'user/post/permissions/', 'user_post_permissions',
                            name='dashboard-api-user-user_post_permissions'),

                        url(r'user/comment/permissions/', 'user_comment_permissions',
                            name='dashboard-api-user-user_comment_permissions'),

                        url(r'user/report/permissions/', 'user_report_permissions',
                            name='dashboard-api-user-user_report_permissions'),

                        url(r'user/remove/comments/(?P<user_id>\d+)', 'removal_comment_user',
                            name='dashboard-api-user-removal-comment-user'),
                        )
