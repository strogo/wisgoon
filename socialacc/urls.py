from django.conf.urls import patterns, include, url

urlpatterns = patterns('socialacc.views',
    #url(r'^$', 'home', name='social-home'),
    url(r'^import_contacts/$', 'import_contacts', name="social-import"),

)

