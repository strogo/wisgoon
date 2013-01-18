from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'elections.views.home', name='election-home'),   
)
