from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.angular.post',
	url(r'^$', 'home', name='angular-home'),
	url(r'^latest/$', 'latest', name='angular-post-latest'),
	url(r'^post/$', 'post', name='angular-post'),
	url(r'^catPage/$', 'catPage', name='angular-catPage'),
	url(r'^EditorPosts/$', 'EditorPosts', name='angular-EditorPosts'),
	url(r'^search/$', 'search', name='angular-search'),
	url(r'^login/$', 'login', name='angular-login'),
	url(r'^register/$', 'register', name='angular-register'),
	url(r'^sendPost/$', 'sendPost', name='angular-sendPost'),
	url(r'^profile/$', 'profile', name='angular-profile'),
	url(r'^likedPost/$', 'likedPost', name='angular-likedPost'),
	url(r'^notifs/$', 'notifs', name='angular-notifs'),
	url(r'^editPost/$', 'editPost', name='edit-post'),
	url(r'^followersList/$', 'followersList', name='followers-list'),
	url(r'^followingsList/$', 'followingsList', name='followings-list'),
	url(r'^editProfile/$', 'editProfile', name='edit-profile'),

	)
