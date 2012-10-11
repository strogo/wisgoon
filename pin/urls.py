from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pin.views',
    url(r'^$', 'home', name='pin-home'),
    url(r'^(?P<item_id>\d+)/$', 'item', name="pin-item"),
    url(r'^send/$', 'send', name="pin-send"),
    url(r'^sendurl/$', 'sendurl', name="pin-sendurl"),
    url(r'^ajax_url/$', 'a_sendurl', name="pin-sendurl-a"),
    url(r'^ajax_upload/$', 'upload', name="pin-upload" ),
    url(r'^comments/posted/$', 'comment_posted'),
)


urlpatterns += patterns('', 
    url(r'^comments/', include('django.contrib.comments.urls')),
)
