from models import CarDoc
import requests
import re
import time

CommuterBBox={"NY": (40.3 ,-75.11, 41.6, -73), "MA": (41, -70, 43, -72)}
APIkey="AsEdtCyDyOQ_b25OlE6p4FAT8svp5S02oMWwwRhDp6F0zmDhE_MTu5bVJYD4EydY"
def warning_to_string(warning):
 	toReturn=" "
 	if str(warning["description"])[-1:]=="-":
		 toReturn=(str(warning["description"] +" Serious Congestion"))
	else:
		 toReturn=(str(warning["description"]))
	try:
		toReturn=toReturn+ " End Date: " + time.ctime(float(warning["end"])/1000)
	except:
		logger.error("end date doesn't exits")
	return toReturn
"""for each city, pull the warnings and add the relevant alerts"""
def pull_and_add_warnings():
	for city in CommuterBBox:
		#api call
		apiCall="http://dev.virtualearth.net/REST/v1/Traffic/Incidents/"
		for point in CommuterBBox[city]:
			apiCall=apiCall+str(point)
			apiCall=apiCall+","
		apiCall=apiCall[:-1]#drop the last comma
		apiCall=apiCall+"/true?inclnb=1&key="+APIkey
		incidents=requests.get(apiCall).json()["resourceSets"][0]["resources"]
		#make all the warnings	
		warnings=list(dict())
		for each in incidents:
			try:
				location=list()
				for code in each["locationCodes"]:
					location.append(str(code))
				warnings.append({"description": each["description"], "severity":each["severity"], "end": each["end"].strip("/").strip("Date(").strip(")"), "locationCodes": location , "roadClosed": each["roadClosed"]})
			except KeyError: #some errors have no location codes
				warnings.append({"description": each["description"], "severity":each["severity"], "end": each["end"].strip("/").strip("Date(").strip(")"), "locationCodes": [None], "roadClosed": each["roadClosed"]})
		#check if the warnings are relevant for each route
		for route in CarDoc.objects(commuterCity=city):
			relevant=list()
			for warning in warnings: 
				if relevant_check(warning, route):
					relevant.append(warning_to_string(warning))

			route.warnings=relevant
			route.save()

"""takes a warning and a route, if the warning is relevant to that Route, true is returned, else false"""
def relevant_check(warning, route):
	#if both in the CarDocs Routes and the Warnings add to the relevant Alerts
	if list(set(warning["locationCodes"])  &  set((route.LocationCodes))):
		return True
	if warning["description"]==None:
		#if there is no description the rest of the checks are useless
		return False
	for street in route.streets:
		if street in warning["description"]:
			return True
	for label in route.labels:
		#this regex needs texting
		if re.search( "(?<![0-9])" + label +  "(?=![0-9])", warning["description"]):
			return True
	return False