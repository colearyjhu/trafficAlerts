from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       #CAMERONTAG
                       url(r'^$', 'transitAlerts.views.home', name='home'),
                       #"""get a route by name"""
                       url(r'^route/(?P<route_name>[^/]+)/$', 'transitAlerts.views.lookupRoute', name='route'),
                       #"""get a route by name with city""""
                       url(r'^route/(?P<route_name>[^/]+)/(?P<city>[^/]+)/$', 'transitAlerts.views.lookupRoute', name='routeAndCity'),
                       #get all the alerts
                       url(r'^alerts/$', 'transitAlerts.views.getAffectedData', name='alerts'),
                       #"""get alerts for a city"""
                       url(r'^alerts/(?P<city>[^/]+)/$', 'transitAlerts.views.getAffectedData', name='alertsForACity'),
                       # Examples:
                       #"""routes for a city"""
                       url(r'^city/(?P<city>[^/]+)/$', 'transitAlerts.views.getCityData', name='city'),
                       #"""routes for a city,with a sort key"""
                       url(r'^city/(?P<city>[^/]+)/(?P<sortKey>\w+)/$', 'transitAlerts.views.getCityData', name='citySorted'),
                       #"""routes for a city, with a sort key, add noalerts to get noalerts"""
                       url(r'^city/(?P<city>[^/]+)/(?P<sortKey>\w+)/(?P<alerts>\w+)/$', 'transitAlerts.views.getCityData', name='citySortedNoAlerts'),
                       
                       url(r'^update/$', 'transitAlerts.views.update', name='update'),
                       
                       url(r'^clear/$', 'transitAlerts.views.clearAlerts', name='clear'),
                       url(r'^build/$', 'transitAlerts.views.buildRoutes', name='build'),
                       url(r'^cars/$', 'transitAlerts.views.carData', name='car'),
                       url(r'^cars/(?P<showMap>[^/]+)$', 'transitAlerts.views.carData', name='car'),
                       url(r'^cars/(?P<start>[^/]+)/(?P<end>[^/]+)/$', 'transitAlerts.views.carData', name='carEndAndStart'),
                       url(r'^cars/(?P<start>[^/]+)/(?P<end>[^/]+)/(?P<showMap>[^/]+)$', 'transitAlerts.views.carData', name='carEndAndStartInbetween'),
                       url(r'^cars/(?P<start>[^/]+)/(?P<end>[^/]+)/(?P<showMap>[^/]+)/(?P<inbetween>[^/]+)$', 'transitAlerts.views.carData', name='carEndAndStartInbetween'),
                       url(r'^incident/$', 'transitAlerts.views.IncidentReportUpdate', name='Incident'),
                       url(r'^commute/(?P<_uid>\w+)/$',                                                         'transitAlerts.views.showAllUserAlerts'),
                       url(r'^commuteMessage/(?P<_uid>\w+)/$',                                                       'transitAlerts.views.seeMessageString'),
                                              ) 
