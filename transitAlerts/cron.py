import cityUpdatesAndBuildFuncs as funcs
import models
import datetime
from geopy import geocoders
import logging
logger = logging.getLogger('wb')


""" """
def updateAlerts():
	for city in funcs.cityUpdate:
		funcs.cityUpdate[city]()
