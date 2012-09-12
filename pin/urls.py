from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pin.views',
    url(r'^$', 'home', name='pin-home'),
    url(r'^send/$', 'send', name="pin-send"),
    url(r'^ajax_upload/$', 'upload', name="pin-upload" ),
)
