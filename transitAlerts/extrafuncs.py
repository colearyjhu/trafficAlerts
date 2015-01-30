"""these are funcs to be added back into sbuscriber or other places after merge"""

  def closestCommuteCity(self): #for WBUSER in subsriccber.models
        try:
            gn=geocoders.GoogleV3()
            place, (commuterlat, commuterlong)=gn.geocode(str(self.profile.zip)) #+ "USA")
            for city in (RouteDoc.objects.distinct("city") + ['New York',]):
                    if len(CityLatLong.objects(city=city))==0:
                        place, (lat, lon)=(gn.geocode(city))
                        CityLatLong(city=city, lat=int(lat), lon=int(lon)).save()
            #set the nearest city by pythagereon thereom
            self.update(set__profile__commuteCity=min(CityLatLong.objects(), key=lambda x: ((int(commuterlat)-int(x.lat))**2+(int(commuterlong)-int(x.lon))**2)).city)
        except Exception, e:
            logger.error(e)

  #CAMERONTAG
def commuteHTMLBeyondNYC(RouteDocs): #formatting.py above commuteHTML
	"""PROTOCOL + HOSTNAME"""
	MoreLink= "http://localhost:8000" + "/beyondnyc_train_status/" + RouteDoc.objects(route_name=RouteDocs[0])[0].city + "/_"
	issues=""
	for name in RouteDocs:
		for route in RouteDoc.objects(route_name=name):
			if "_" + route.route_name + "_" in MoreLink:
				continue
			MoreLink += route.route_name +'_'
			if route.alert!=dict():
				issues+=str(route.route_name)+ " "

	
	if len(issues) <= 0:
		html =	"<td style='font-size: 10px; -webkit-text-size-adjust:none; background: transparent;'>"  \
					"<div class='commute-block' width='100%'>"	\
						"<p style='font-size: 10px; margin: 0 auto; font-size: 1.6em; line-height: 1.4em;  -webkit-margin-before: 0; -webkit-margin-after: 0;'>As of " 	\
							+  str(RouteDoc.objects(route_name=RouteDocs[0])[0].updateTime.strftime("%m/%d/%Y %I:%M %p")) +	\
					 		", there were no issues."	\
					 	"</p>"	\
					"</div>"	\
				"</td>"
	else:
		html = 	"<td style='font-size: 10px; -webkit-text-size-adjust:none; background: transparent;'>"  \
					"<div class='commute-block' width='100%'>"	\
						+ issues +	\
						"<p style='font-size: 10px; margin: 1em auto 0; font-size: 1.2em; line-height: 1.2em; -webkit-margin-after: 0; text-transform: uppercase;'>"	\
							"<a style='color: #7374ad; text-decoration: underline;' href='" + MoreLink + "' target='_blank'>"	\
								"<span style='float: none; font-weight: bold; white-space: nowrap;' class='more'>Delays & Changes</span>"	\
							"</a> as of "	\
							+ str(RouteDoc.objects(route_name=RouteDocs[0])[0].updateTime.strftime("%m/%d/%Y %I:%M %p")) +	\
						"</p>"	\
	 				"</div>"	\
 				"</td>"
 	return cardHTML('commute', html)

 	urls


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
    (r'^commute/(?P<_uid>\w+)/$',                                                         'transitAlerts.views.showAllUserAlerts'),
    (r'^commuteMessage/(?P<_uid>\w+)/$',                                                       'transitAlerts.views.seeMessageString'),
    (r'^beyondnyc_train_status/(?P<city>[^/]+)/(?P<_lines>[^/]+)/',                                             'thirdpartyapis.views.beyondnyc_train_status'),