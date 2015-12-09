from django.conf.urls import patterns, url

urlpatterns = patterns('pin.views2.dashboard.api.dashboard_home',
                       url(r'$', 'home', name='dashboard-api-home'),
                       )
