import xml.etree.ElementTree as ET #chicago is XML
import subprocess
import os
import json
from mongoengine import *
import requests
from models import RouteDoc
import re
import pytz
import datetime

import logging
logger = logging.getLogger('wb')

"""constant urls for alerts by city, used to pull current transit alerts"""

alertURL={"Chicago": "http://www.transitchicago.com/api/1.0/alerts.aspx", 
"DCbus":"http://www.metroalerts.info/rss.aspx?bus", "DCtrain": "http://www.metroalerts.info/rss.aspx?rs", #http://web.archive.org/web/20140703175532/http://www.metroalerts.info/rss.aspx?rs
"Boston": "http://realtime.mbta.com/developer/api/v1/alerts?api_key=qiw9Uj1r6UCTazmwZiOw6g",
"San Franciso": {"BART" :  "http://www.bart.gov/schedules/advisories/advisories.xml"}, #"http://web.archive.org/web/20110626003657/http://www.bart.gov/schedules/advisories/advisories.xml"},
"Philadelphia": "http://www3.septa.org/hackathon/Alerts/get_alert_data.php?req1=all",
"New York": "http://web.mta.info/status/serviceStatus.txt",
 }

"""the files that each routes GTFS is pulled from"""

GTFSfile={"Chicago": "transitAlerts/Chicago_GTFS/routes.txt", "Boston": "transitAlerts/MBTA_GTFS/routes.txt", 
"DC": "transitAlerts/DC_GTFS/routes.txt", "San Franciso": "transitAlerts/SanFran_GTFS/routes.txt", "Philadelphia": "transitAlerts/SEPTA_GTFS/routes.txt",
"New York" : "transitAlerts/NY_GTFS/routes.txt"}


"""function for updating alerts for New York City RouteDocs.Parses Real Time alerts from alertURL[New York]"""
def NY_add_alerts():
	"""see if the file is retrievable if so then clear down all the alerts"""
	try:
		alertData=ET.fromstring(requests.get(alertURL["New York"]).content)
		time=datetime.datetime.utcnow()
		time=time + pytz.timezone('US/Eastern').utcoffset(time)
		for route in RouteDoc.objects(city="New York"):
			route.alert= None
			route.updateTime=time
			route.save()
	except (ET.ParseError, requests.exceptions.ConnectionError):
		logger.error("Your url for alertURL[New York] is useless")
		return
 	#for all the subway lines
	for group in alertData.findall("subway/line"):
		#if there's good service we don't care
		if  group.find("status").text=="GOOD SERVICE":
			continue
		#instantiate the 3 variables
		effect=group.find("status").text
		description=re.sub('&nbsp;',' ', re.sub('<[^<]+?>', '', group.find("text").text))
		url="http://www.mta.info/subway/"+group.find("name").text
		#for every subway line in the group, alerts are organized by groups such as ACE or 123 trains 
		for line in group.find("name").text:
			#if that line is in the description, add an alert
			if "[" + line + "]" in description:
				try: 
					RouteDoc.objects.get(city="New York", route_name=str(line)).add_alert(effect, description, url)
				except:
					logger.error("New York doesn't have line" + line)
	#straightforward for LIRR
	for line in alertData.findall("LIRR/line"):
		if  line.find("status").text=="GOOD SERVICE":
			continue
		effect=line.find("status").text
		description=re.sub('&nbsp;',' ', re.sub('<[^<]+?>', '', line.find("text").text))
		url="http://www.mta.info/LIRR/" + line.find("name").text
		try:
			RouteDoc.objects.get(city="New York", route_name=line.find("name").text).add_alert(effect, description, url)
		except:
			logger.error("New York doesn't have line " + str(line))
	#straightforward for MNR
	for line in alertData.findall("MetroNorth/line"):
		if  line.find("status").text=="GOOD SERVICE":
			continue
		effect=line.find("status").text
		description=re.sub('&nbsp;',' ', re.sub('<[^<]+?>', '', line.find("text").text))
		url="http://www.mta.info/MNR/" + line.find("name").text
		try:
			RouteDoc.objects.get(city="New York", route_name=line.find("name").text).add_alert(effect, description, url)
		except:
			logger.error("New York doesn't have line " + str(line))

	#for every bus, line numbers between certain values are given. We try and add routes for every relevant bus in the RANGE of values given
	for group in (alertData.findall("bus/line")):
		if group.find("status").text=="GOOD SERVICE":
			continue
		effect=group.find("status").text
		description=re.sub('&nbsp;',' ', re.sub('<[^<]+?>', '', group.find("text").text))
		url="http://www.mta.info/bus/"+(group.find("name").text.strip())
		#the letter prefix of the route
		letter=re.findall('[a-zA-Z]*', group.find("name").text)[0]
		#get the two numbers in the range
		numbers=[int(s) for s in re.findall('[1-9]*', group.find("name").text) if s.isdigit()]
		#for every line in the range
		for line in range(numbers[0],numbers[1]):
			if (letter+str(line)) not in description:
				continue
			try:
				RouteDoc.objects.get(city="New York", route_name=letter+str(line)).add_alert(effect, description, url)
			except:
				logger.error("New York doesn't have line" + letter + str(line))

"""function for updating alerts for San Franciso RouteDocs.Parses Real Time alerts from alertURL[San Franciso]"""
def sanFran_add_alerts():
	try:
		alertData=ET.fromstring(requests.get(alertURL["San Franciso"]["BART"]).content)
		time=datetime.datetime.utcnow()
		time=time + pytz.timezone('US/Eastern').utcoffset(time)
		for route in RouteDoc.objects(city="San Franciso"):
			route.alert= None
			route.updateTime=time
			route.save()
	except (ET.ParseError, requests.exceptions.ConnectionError):
		logger.error("Your url for alertURL[San Franciso] is useless")
		return
	for alert in alertData.findall("channel/item"):
		#get the url description and effect
		url=alert.find("link").text
		description=alert.find("description").text
		effect=alert.find("title").text
		#get the services Impacted by the above.
		ImpactedService=alert.find("ImpactedService")
		#get thier ids
 		for doc in RouteDoc.objects(city="San Franciso"):
 		#SHOULD BE INCORPORATED INTO ABOVE FOR LOOP
 			if "BART" not in doc.route_id:
 				continue
 			for name in doc.route_name.split("-"):
 				if name in description:
 					doc.add_alert(effect, description, url)
 				if name in description.replace(" /", ""):
 					doc.add_alert(effect, description, url)
"""function for updating alerts for Philly RouteDocs.Parses Real Time alerts from alertURL[New]"""
def philadelphia_add_alerts():
	try:
			alertData=requests.get(alertURL["Philadelphia"]).json()
			time=datetime.datetime.utcnow()
			time=time + pytz.timezone('US/Eastern').utcoffset(time)
			for route in RouteDoc.objects(city="Philadelphia"):
				route.alert= None
				route.updateTime=time
				route.save()
	except (ValueError, requests.exceptions.ConnectionError):
		logger.error("Your url for alertURL[Philadelphia] is useless")
		return
	#adds the alerts to the approriate routes
	for alert in alertData:
		try:
			routeAffected=RouteDoc.objects.get(city="Philadelphia", route_id=alert["route_name"].replace("/", " "))
		except  RouteDoc.DoesNotExist:
			try:
				routeAffected=RouteDoc.objects.get(city="Philadelphia", route_name=(alert["route_name"].replace("/", " ") + " Line"))
			except RouteDoc.DoesNotExist:
				logger.error("SEPTA file doesn't have route:" + alert["route_name"])
				continue
		except KeyError:
				logger.error("SEPTA error not added:" +  str(alert) + "\n")
				continue	

		if alert["current_message"]!="":
			routeAffected.add_alert("delay or other", re.sub('<[^<]+?>', '', alert["current_message"]), "www.septa.org")
		elif alert["advisory_message"]!="":
				routeAffected.add_alert("advisory",re.sub('<[^<]+?>', '', alert["advisory_message"]), "www.septa.org")
		elif alert["detour_message"]!="":
				routeAffected.add_alert("detour",re.sub('<[^<]+?>', '', alert["detour_message"]), "www.septa.org")
		

"""function for adding alerts from the Chicago alerts file, logger error if a route an alert is for, doesn't exist in the given routes"""
def chicago_add_alerts():
	try:
		alertData= ET.fromstring(requests.get(alertURL["Chicago"]).content)
		time=datetime.datetime.utcnow()
		time=time + pytz.timezone('US/Eastern').utcoffset(time)
		for route in RouteDoc.objects(city="Chicago"):
			route.alert= None
			route.updateTime=time
			route.save()
	except (ET.ParseError, requests.exceptions.ConnectionError):
		logger.error("Your url for alertURL[Chicago] is useless")
		return
	#parses the XML tree and adds the Alert to the right Routes
	#for every alert
	for alert in alertData.findall("Alert"):
		#get the url description and effect
		url=alert.find("AlertURL").text
		description=alert.find("ShortDescription").text
		effect=alert.find("Headline").text
		#get the services Impacted by the above.
		ImpactedService=alert.find("ImpactedService")
		#get thier ids
		for serviceId in ImpactedService.findall(".Service/ServiceId"):
			#add the alerts
			try:
				routeAffected=RouteDoc.objects.get(city="Chicago", route_id=serviceId.text)
				routeAffected.add_alert(effect, description, url)
			except  RouteDoc.DoesNotExist:
				logger.error("Chicago has no route:" + serviceId.text +  "alert was"+ url+ description + effect + "\n")
			except AttributeError:
				logger.error("Chicago route had no serviceID  alert was"+ url+ description + effect + "\n")

				
"""function for adding alerts from the DC alerts file, logger error if a route an alert is for, doesn't exist in the given routes"""
def dc_add_alerts():
	try:
		time=datetime.datetime.utcnow()
		time=time + pytz.timezone('US/Eastern').utcoffset(time)
		for route in RouteDoc.objects(city="DC"):
			route.alert= None
			route.updateTime=time
			route.save()
		dc_addAlert_subroutine(requests.get(alertURL["DCbus"]).content)
		dc_addAlert_subroutine(requests.get(alertURL["DCtrain"]).content)
	except requests.exceptions.ConnectionError:
		logger.error("tried really hard but that file doesn't exist")

"""function for parsing the xml structure for a DC alerts RSS file(plural files but this function only reads one).
	 called twice by parent function for buses and then trains"""
def dc_addAlert_subroutine(string):
	try:
		alertData= ET.fromstring(string)
	except ET.ParseError:
		logger.error("Your url for alertURL[DC] is useless")
		return
	#parses the XML tree and adds the Alert to the right Routes
	for alert in alertData.findall(".channel/item"):
			url=alert.find("link").text
			description=alert.find("description").text
			effect=alert.find("source").text
			ImpactedService=alert.find("title")
			servicesIdImpacted=ImpactedService.text.split(", ")
			for serviceId in servicesIdImpacted:			
				#add the alerts
				try:
					routeAffected=RouteDoc.objects.get(city="DC", route_name=serviceId)
					routeAffected.add_alert(effect, description, url)
				except RouteDoc.DoesNotExist:
					try:
						routeAffected=RouteDoc.objects.get(city="DC", route_name=serviceId.title())
						routeAffected.add_alert(effect, description, url)
					except: 
						#if the route isn't in the GTFS document say so
						logger.error("DC has no route:" + serviceId + "\n")
					

"""function for adding alerts from the boston alerts file, logger error if a route an alert is for, doesn't exist in the given routes"""
def boston_add_alerts():
	try:
		alertData=requests.get(alertURL["Boston"]).json()
		time=datetime.datetime.utcnow()
		time=time + pytz.timezone('US/Eastern').utcoffset(time)
		for route in RouteDoc.objects(city="Boston"):
			route.alert= None
			route.updateTime=time
			route.save()
	except (ValueError, requests.exceptions.ConnectionError):
		logger.error("Your url for alertURL[Boston] is useless")
		return
	#adds the alerts to the approriate routes
	for alert in alertData["alerts"]:
		for services in alert["affected_services"]["services"]:
			try:
				routeAffected=RouteDoc.objects.get(city="Boston", route_id=services["route_id"])
				routeAffected.add_alert(alert["effect_name"],alert["description_text"], "mbta.com") #url was deleted by mbta
			except KeyError:
					logger.error("MBTA error not added:" +  str(alert) + "\n")	
			except RouteDoc.DoesNotExist:
					logger.error("MBTA file doesn't have route" + services["route_id"])			

"""constants, gives the alert update method and routes.txt file for known cities, adding a city needs 3 edits,
one here one up top for the alert-URL and one up top in GTFS-URL"""
cityUpdate={"Boston": boston_add_alerts, "Chicago": chicago_add_alerts, "DC": dc_add_alerts, "San Franciso": sanFran_add_alerts, "Philadelphia": philadelphia_add_alerts, "New York": NY_add_alerts}

def city_validation():
	"""makes sure that there is  an update function and a gtfs file for all """	
	for city in GTFSfile:
		try:
			cityUpdate[city]
		except KeyError:
			return False

	return True

route_type={"0": "Light_Rail", "1": "Subway", "2": "Train", "3": "Bus", "4": "Ferry", "5" : "Cable" }
def buildDocs():
	"""makes the routes( from routes.txt files from GTFS)"""
	for city in GTFSfile:
		try:
			route_file=open(GTFSfile[city], 'r')
			logger.info(city + " opened")
		except IOError:
			logger.error(city + "GTFS file does not exist")
			continue
		routes=dict()
		line_list=route_file.readlines()
		route_file.close()
		for line in line_list:
			line=line.replace('"', "")
			line=line.replace('\'', "")
			line=line.replace('/', " ")
			#skips the first line headers
			if "route_id" in line:
				continue
			CSV_list=line.split(',')


			"""FROM HERE UNTIL MARKER ARE IF STATEMENTS TO REMEDY THE DEVIATIONS FROM GTFS OF THE VARIOUS TRANSIT SYSTEMS"""
			if city is "DC":
				CSV_list[5]=CSV_list[4] #DC just cannot listen to directions
				if CSV_list[5]=="1":
					CSV_list[3]=CSV_list[2] 

			if CSV_list[1]=="BART":#differentiate bart from SMFS
				if "BART" not in CSV_list[0]:
					CSV_list[0]+=" BART"
			if city=="Chicago":
				CSV_list[5]=CSV_list[3] #chicago either
			if city=="Philadelphia" and (CSV_list[5]=="" or CSV_list[5]=="000000" or CSV_list[5]=="FFFFFF"):
				#philly has two Route files with slight differences, I concatenate the two.
				CSV_list[5]=CSV_list[3]
			if city=="Philadelphia":
				CSV_list[0]=CSV_list[1]#hacky way to get bus ids instead of random numbers
			if city =="New York":#fix differences between the different authorities and add the type of line to the route_id
				if CSV_list[1]=="MTA NYCT":
					CSV_list[3]=CSV_list[0]
					if CSV_list[5]!="3":
						CSV_list[5]=CSV_list[4]
						CSV_list[0]+="Subway"
					else:
						CSV_list[0]+="bus"
				elif CSV_list[1]=="LIRR":
					CSV_list[5]=CSV_list[4]
					CSV_list[0]+="LIRR"
			"""MARKER"""		

			#turns route type, which is currently a number, into the corresponding name of type of route, makes something a "line" given a lack of info
			CSV_list[5]=route_type.get(CSV_list[5].replace(" ",""), CSV_list[5]+ "Line")
			#the GTFS CSV placement for routeId, routeName and routeType. routeName can be short or long, long is preffered if it exists(long is CSV[3], but some cities switches them hence the length call)
			if CSV_list[3].isspace() or CSV_list[3]=="\"\"" or CSV_list[3]=="" or len(CSV_list[2])>len(CSV_list[3]):
				CSV_list[3]=CSV_list[2]
			try:	
				#try to jsut update an existing route, but if not there just save
				RouteDoc.objects.get(route_id=CSV_list[0], city=city).update(set__route_id=CSV_list[0], set__route_name=CSV_list[3], set__route_type=CSV_list[5], set__city=city, set__alert=dict())
			except (RouteDoc.DoesNotExist, KeyError):
				RouteDoc(route_id=CSV_list[0], route_name=CSV_list[3], route_type=CSV_list[5], city=city, alert=dict()).save()
			except exception, e: logger.error(str(e))
