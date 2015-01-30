from django.db import models

from mongoengine import *
import json
import requests
import datetime
import pytz
import logging
logger = logging.getLogger('wb')

class RouteDoc(Document):
		route_id=StringField(required=True, unique_with='city')
		route_name=StringField(required=True)
		route_type=StringField(required=True)
		city=StringField(required=True)
		alert=DictField()
		updateTime=DateTimeField()

		def json_service_alert(self):
			return json.dumps({ "route": { "route_id": self.route_id, "route_name":self.route_name, "route_city": self.city, "route_type": self.route_type, "alert": self.alert }})	
		def json_route(self):
			return json.dumps({ "route": { "route_id": self.route_id, "route_name":self.route_name, "route_city": self.city, "route_type": self.route_type }})

		def add_alert(self, effect,description,moreInfo):
			self.alert={"effect": effect,"description": description,"moreInfo": moreInfo}
			self.save()





















"""specifies a route for cars, initializes with a start and end point and can have via points(called:inbetween)"""
class CarDoc(Document): 
	start=StringField(required=True, unique_with='end')
	end=StringField(required=True, unique_with='start')
	inbetween=ListField(StringField(), required=False)
	APIkey="AsEdtCyDyOQ_b25OlE6p4FAT8svp5S02oMWwwRhDp6F0zmDhE_MTu5bVJYD4EydY"
	url=StringField()
	imageUrl=StringField()
	json=DictField()#the json returned from the api call
	commuterCity=StringField()#currently actually state
	delayTime=IntField()#minutes
	updateTime=DateTimeField()
	expectedTravelTime=IntField()#minutes
	instructions=ListField(DictField())#basic unit of directions API, same as say GPS instructions(turn left here sally) but with all the meta data too.
	warnings=ListField(StringField())#warnings instantiated by the bounding box
	warningsFromIndividual=ListField(StringField())#warnings instantiated from the directions api
	streets=ListField(StringField())#street names
	labels=ListField(StringField())#labels are route numbers like I-95, RT-35
	LocationCodes=ListField()#like hashes, designated by bing. 

	"""THIS IS A NECESSARY INTLIZATION METHOD, can also be used to update info, False is returned if it fails"""
	def initialization(self):
		#create the api call URL
		directionString="http://dev.virtualearth.net/REST/V1/Routes/Driving?o=json&wp.0="+self.start
		count=1
		for viaPoint in self.inbetween:
			directionString=directionString+"&wp." + str(count) + "="+ viaPoint
			count=count+1
		directionString=directionString+"&wp." + str(count) + "="+ self.end+ "&key="+self.APIkey
		#get the json, stripped of fluff
		try:
			self.json=requests.get(directionString).json()["resourceSets"][0]["resources"][0]
		except (requests.exceptions.ConnectionError, IndexError):
			logger.error("Route did not initialize route start: "+ self.start + "route end: " + self.end + "route destroyed")
			return False
		#take some of json and put it in database
		self.expectedTravelTime=self.json["travelDurationTraffic"]/60
		self.delayTime=(self.expectedTravelTime*60 - self.json["travelDuration"]) /60
		#add all the instructions to the database
		instructions=list()
		for direction in self.json["routeLegs"][0]["itineraryItems"]:
			instructions.append(direction)
		self.instructions=instructions
		#metro area in question
		try:
			self.commuterCity=self.json["routeLegs"][0]["endLocation"]["address"]["adminDistrict"]
		except KeyError:
			logger.error("no commuter city to add route destroyed")
			return False
		#update time
		time=datetime.datetime.utcnow()
		time=time + pytz.timezone('US/Eastern').utcoffset(time)
		self.updateTime=time
		#used for easy site navigation
		self.url= "/cars/" + self.start + "/" + self.end + "/" + "yes"
		#make the image url.
		self.imageUrl="http://dev.virtualearth.net/REST/v1/Imagery/Map/Road/Routes?wp.0="+self.start+ "&wp.1=" + self.end + "&key="+self.APIkey
		#if there's a way point add it to the url as well
		if self.inbetween:
			self.url=self.url  + ' '.join(self.inbetween)
		#add the warnings streets and location Codes to Database
		self.instruction_parse()
		return True

	""" takes the instructions from the routes and adds the current warnings streets and Location Codes to the database"""
	def instruction_parse(self):
		if len(self.instructions) == 0:
			logger.error("No Instructions to parse for route starting at" + self.start + "and ending at" + self.end)
			return
		LocationCodes=list()
		warnings=list()
		streets=list()
		labels=list()
		for instruction in self.instructions:
			try:
				#add the name of the route and it's location codes to the dict
				for code in instruction["details"][len(instruction["details"])-1]["locationCodes"]:
					LocationCodes.append((code).encode('utf-8'))
			except KeyError:
				pass #if location codes don't exist we don't care
			try:
				for warning in instruction["warnings"]:
					newWarning=warning["text"] + " on "
					newWarning=newWarning+(instruction["details"][len(instruction["details"])-1]["names"][0]).encode('utf-8')
					warnings.append(newWarning)
			except KeyError:
				pass #if a warning doesn't exist we don't care
			try:
				for street in instruction["details"][len(instruction["details"])-1]["names"]:
					street=street.encode('utf-8')
					#bing switches back to Pky for GeoCoding
					if "Pkwy" in street:
						street=street.replace("Pkwy", "Pky")
					streets.append(street)
			except KeyError:
				pass #if street names don't exist we don't care
			try:
				for label in instruction["details"][len(instruction["details"])-1]["roadShieldRequestParameters"]["shields"][0]["labels"]:
					labels.append((label.encode('utf-8')))
			except KeyError:
				pass 
		self.warningsFromIndividual=warnings
		self.LocationCodes=LocationCodes
		self.streets=streets
		self.labels=labels
		self.save()
