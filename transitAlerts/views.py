# Create your views here.

from django.shortcuts import render
from django.template import RequestContext, loader
from models import RouteDoc, CarDoc
import carTraffic
import cityUpdatesAndBuildFuncs as funcs
import datetime
from django.http import HttpResponse
import urls 

import pytz
import cron

#from subscriber.models import *


def home(request):
	context={"title": "Welcome to Alert Viewer"}
	return render(request, 'AlertViewer.html', context)


def showAllUserAlerts(request, _uid):
    # show email view for user
    u = WBUser.getUser(_uid)

    if u is None:
        return render(request, 'AlertViewer.html', context)
    routecontext=list()
    for route in u.profile.otherRoutes:
    	routecontext+=(RouteDoc.objects(city=u.profile.commuteCity, route_name=route))
    logger.error(routecontext)
    context={'routes' : routecontext, 'title' : "your routes"}
    return render(request, 'AlertViewer.html', context)


def lookupRoute(request, route_name, city=None, sortKey="route_id"):
	if city is not None:
		try:
			routes = RouteDoc.objects(route_name=route_name.title(), city=city.title())
		except:
			logger.error("route doesn't exist")
			return
		""""some non standard catches, like DC being all capitals, CR-* for commuter rail in boston having weird capitlization""" 
		if len(routes)==0:
			routes = RouteDoc.objects(route_name=route_name.title(), city=city.upper())
		if len(routes)==0:
			routes = RouteDoc.objects(route_name=route_name, city=city.upper())
		if len(routes)==0:
			routes = RouteDoc.objects(route_name=route_name, city=city.title())
	else:
		routes = RouteDoc.objects(route_name=route_name.title())
	context={'routes' : routes, 'title' : route_name}
	return render(request, 'AlertViewer.html', context)


def getCityData(request, city, sortKey="alert", alerts=True):
	routes = RouteDoc.objects(city=city.title())
	if len(routes)==0:
		#dc needs all uppercase
		routes = RouteDoc.objects(city=city.upper())
	route_string=""

	try:
		if sortKey is "alert":
			routes= sorted(routes, key=lambda routes: routes[sortKey],  reverse=True)
		else:
			routes= sorted(routes, key=lambda routes: routes[sortKey])
	except KeyError:
		#if thats not a real key just sort by route_id
		routes= sorted(routes, key=lambda routes: routes["route_id"])
	context={'routes' : routes, 'title': city}
	return render(request, 'AlertViewer.html', context)

def getAffectedData(request, city=None, sortKey="city"):
	if city is None:
		routes = RouteDoc.objects(__raw__={'alert.effect':  {'$exists' :True}})
	else:
		routes = RouteDoc.objects(__raw__={'alert.effect':  {'$exists' :True}}, city=city.title())
		if len(routes)==0:
		#dc needs all uppercase
			routes = RouteDoc.objects(__raw__={'alert.effect':  {'$exists' :True}}, city=city.upper())
	route_string=""
	try:
		routes= sorted(routes, key=lambda routes: routes[sortKey])
	except KeyError:
		#if thats not a real key just sort by route_id
		routes= sorted(routes, key=lambda routes: routes["route_id"])
	if city is None:
		context={'routes' : routes, "title": "Alerts for all Cities"}
	else:
		context={'routes' : routes, "title": "Alerts for " + city}
	return render(request, 'AlertViewer.html', context)

def update(request):
	cron.updateAlerts()
	message = str(len(RouteDoc.objects())) + " routes updated \n" 
	for city in funcs.GTFSfile.keys():
		message +=  city + " has this many alerts " + str(len(RouteDoc.objects(__raw__={'alert.effect':  {'$exists' :True}}, city=city))) + \
		" and this many routes " + str(len(RouteDoc.objects(city=city))) + "\n the following route types, their count and their alert count \n"

		for transportType in funcs.route_type.values():
			message+= transportType + ": count " + str(len(RouteDoc.objects(city=city, route_type=transportType))) + \
			" alerts " + str(len(RouteDoc.objects(__raw__={'alert.effect':  {'$exists' :True}}, city=city, route_type=transportType))) + "\n"

	context={"title": "Results",  "message": message}
	return render(request, 'update.html', context)

def clearAlerts(request):
	for route in RouteDoc.objects():
		route.alert=None
		RouteDoc.save(route)
	context= {"title": "Results", "message": (str(len(RouteDoc.objects())) + " routes cleared")}
	return render(request, 'update.html', context)

def buildRoutes(request):
	funcs.buildDocs()
	context={"title": "Results", "message": (str(len(RouteDoc.objects())) + " routes created")}
	return render(request, 'update.html', context)

def IncidentReportUpdate(request):
	carTraffic.pull_and_add_warnings()
	context={"title": "All Routes in Database", "routes": CarDoc.objects()}
	return render(request, 'cars.html', context)

def seeMessageString(request, _uid):
	u = WBUser.getUser(_uid)
	if u is None:
		return render(request, 'update.html', context)
	context={"title": "your alerts",  "message": u.otherCommuteString()}
	return render(request, 'update.html', context)



def carData(request, start=None, end=None, showMap=False, inbetween=None):
	if showMap=="no": #gives a way not to show the map
		showMap=False
	if inbetween is not None:
		raise Exception("Nope")
		inbetween=inbetween.split()
	if start is None or end is None:
		context={"title": "All Routes in Database", "routes": CarDoc.objects(), "showMap": showMap }
		return render(request, 'cars.html', context)
	title="Route"
	inquestion, created=CarDoc.objects.get_or_create(start=start, end=end)
	""" if intilization doesn't work, false is returned"""
	if (not inquestion.initialization()):
		inquestion.delete()
		return render(request, 'cars.html', {"title": "Invalid Route"})
	context={"title": title, "routes": [inquestion], "showMap": showMap }
	return render(request, 'cars.html', context)

