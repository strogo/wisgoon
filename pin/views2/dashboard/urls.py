from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.dashboard.home',
                       url(r'$', 'home', name='dashboard-home'),                       
)

