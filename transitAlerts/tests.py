from models import CarDoc, RouteDoc
from mongorunner import TestCase
import logging
from mongoengine import *
import unittest
import cityUpdatesAndBuildFuncs as funcs
import cron
import carTraffic

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class TransitTest(TestCase):

	"""test that Building and updating works as it shoud """
	def test_build_and_update(self):
		"""MACROS FOR TESTING"""
		ROUTE_DOC_SIZE_AFTER_BUILD=600
		ROUTE_TYPE_POSSIBILLITIES=funcs.route_type.values()
		cities=funcs.GTFSfile.keys()
		"""build"""
		self.assertEqual(len(RouteDoc.objects()), 0)
		self.assertTrue(funcs.city_validation(), msg="GTFS files and alerts files not matching up")
		funcs.buildDocs()
		for city in cities:
			"""make sure 1 less than line count cites are created"""
			route_file=open(funcs.GTFSfile[city], "r")
			#cheating becuase New York route doc is combination of 5, mostly similar docs
			if city!='New York':
				self.assertEqual(len(RouteDoc.objects(city=city)), len(route_file.readlines())-1)
			route_file.close()
		for route in RouteDoc.objects():
			self.assertEqual(route.alert, dict(), msg="alerts are not instantiatizing to blank dicts")
			self.assertEqual(route.updateTime, None, msg="update time not instantiatizing to none")
			self.assertTrue(route.route_type in ROUTE_TYPE_POSSIBILLITIES, msg="route type not converting, (could also not been added to test list)" + route.route_type)
		"""update"""
		cron.updateAlerts()
		for route in RouteDoc.objects():
			self.assertNotEqual(route.updateTime, None, msg="routes aren't updating")
		for city in cities:
			self.assertTrue(len(RouteDoc.objects(__raw__={'alert.effect':  {'$exists' :True}}, city=city))>0, city)		
	"""test that all the Routes in alertsExpected.txt have alerts"""
	def test_alert_exists(self):
		try: 
			alert_file=open("alertsExpected.txt", "r")
		except:
			return
		noAlerts=list()
		for line in alert_file.readlines():
			line=line.strip()
			line=line.strip(" ")
			CSV_list=line.split(",")
			try:
				if RouteDoc.objects.get(city=CSV_list[0], route_name=CSV_list[1]).alert!=dict():
					continue
				else:
					noAlerts.append(line)
			except:
				self.assertTrue(False, msg=CSV_list)

		alert_file.close()
		self.assertEqual(len(noAlerts), 0, msg="routes with no alerts " + str(noAlerts))



class CarTest(TestCase):

	def test_make_a_route_and_geo_code(self):
		self.assertEqual(len(CarDoc.objects()), 0)
		MyHouse=CarDoc.objects.create(start="10514", end= "10001")
		BostonRoute=CarDoc.objects.create(start="walpol", end="Boston")
		carTraffic.pull_and_add_warnings()
		CarDoc.drop_collection()
		


	def test_route_name_handeling(self):
		self.assertEqual(len(CarDoc.objects()), 0)
		testSubject=CarDoc.objects.create(start="14 chappaqua place", end= "10001")#doesn't exist, but town does
		self.assertTrue(not testSubject.initialization())
		testSubject=CarDoc.objects.create(start="14 whitlaw close", end= "NYC")#does exist
		self.assertTrue(testSubject.initialization())
		testSubject=CarDoc.objects.create(start="london", end="Paris")#should work, but has accent mark roads
		self.assertTrue(testSubject.initialization())
		testSubject=CarDoc.objects.create(start="san franciso", end="St. Petersburg")#real places but no road connection
		self.assertTrue(not testSubject.initialization())
		CarDoc.drop_collection()

