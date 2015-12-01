from django.conf.urls import patterns, url

urlpatterns = patterns('pin.api6.auth',
                       url(r'auth/register/$', 'register', name='api-6-auth-register'),
                       url(r'auth/login/$', 'login', name='api-6-auth-login'),
                       url(r'auth/logout/$', 'logout', name='api-6-auth-logout'),
                       url(r'auth/follow/$', 'follow', name='api-6-auth-follow'),
                       url(r'auth/unfollow/$', 'unfollow', name='api-6-auth-unfollow'),
                       url(r'auth/followers/(?P<user_id>\d+)/$', 'followers', name='api-6-auth-followers'),
                       url(r'auth/following/(?P<user_id>\d+)/$', 'following', name='api-6-auth-following'),
                       url(r'auth/user/(?P<user_id>\d+)/$', 'profile', name='api-6-auth-profile'),
                       url(r'auth/user/update/$', 'update_profile', name='api-6-auth-profile-update'),
                       url(r'auth/user/search/$', 'user_search', name='api-6-auth-user-search'),
                       url(r'^auth/user/(?P<user_id>\d+)/likes/$', 'user_like', name='api-6-auth-user-like')
                       )

urlpatterns += patterns('pin.api6.post',
                        url(r'post/latest/$', 'latest', name='api-6-post-latest'),
                        url(r'post/choices/$', 'choices', name='api-6-post-choices'),
                        url(r'post/friends/$', 'friends', name='api-6-post-friends'),
                        url(r'post/category/(?P<category_id>\d+)/$', 'category', name='api-6-post-category'),
                        url(r'post/item/(?P<item_id>\d+)/$', 'item', name='api-6-post-item'),
                        url(r'post/search/$', 'search', name='api-6-post-search'),
                        url(r'post/report/(?P<item_id>\d+)/$', 'report', name='api-6-post-report'),
                        url(r'post/edit/(?P<item_id>\d+)/$', 'edit', name='api-6-post-edit'),
                        url(r'post/send/$', 'send', name='api-6-post-send'),
                        url(r'post/user/(?P<user_id>\d+)/$', 'user_post', name='api-6-post-user'),
                        url(r'post/related/(?P<item_id>\d+)/$', 'related_post', name='api-6-post-related'),
                        url(r'post/promoted/$', 'promoted', name='api-6-post-promoted'),
                        url(r'post/hashtag/$', 'hashtag', name='api-6-post-hashtag'),
                        )

urlpatterns += patterns('pin.api6.comment',
                        url(r'comment/showComments/post/(?P<item_id>\d+)/', 'comment_post', name='api-6-comment-post'),
                        url(r'comment/add/post/(?P<item_id>\d+)/$', 'add_comment', name='api-6-comment-add'),
                        url(r'comment/delete/(?P<comment_id>\d+)/$', 'delete_comment', name='api-6-comment-delete'),
                        )

urlpatterns += patterns('pin.api6.like',
                        url(r'like/post/(?P<item_id>\d+)/$', 'like_post', name='api-6-like-post'),
                        url(r'like/likers/post/(?P<item_id>\d+)/$', 'post_likers', name='api-6-likers-post'),
                        )

urlpatterns += patterns('pin.api6.notification',
                        url(r'notif/count/$', 'notif_count', name='api-6-notif-count'),
                        url(r'notif/$', 'notif', name='api-6-notif-notif'),
                        )

urlpatterns += patterns('pin.api6.urlsMap',
                        url(r'urls/$', 'show_map', name='api-6-urls-map'),
                        )

urlpatterns += patterns('pin.api6.category',
                        url(r'category/(?P<cat_id>\d+)/$', 'show_category', name='api-6-category'),
                        url(r'category/all/$', 'all_category', name='api-6-categoreis'),
                        )
