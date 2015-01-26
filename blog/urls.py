from django.conf.urls import patterns, include, url
from django.contrib import admin
from feedreader.api import UserResource

admin.autodiscover()

user_resource = UserResource()

urlpatterns = patterns('blog.views',
    url(r'^$', 'home', name='blog-home'),
    url(r'^post/(?P<id>\w+)/$', 'view_post', name='blog-view-post'),
    url(r'^admin/$', 'admin', name='blog-admin'),
    url(r'^submit/$', 'submit', name='blog-submit'),
    url(r'^edit/(?P<id>\w+)/$', 'edit', name='blog-edit'),
    url(r'^tag/(?P<tag_name>.*)/$', 'tag', name='blog-tag'),
)