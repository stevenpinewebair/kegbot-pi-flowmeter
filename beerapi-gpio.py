import requests
import json

import RPi.GPIO as GPIO
import os, sys, math, logging
import time
import datetime
from threading import Timer
#from datetime import datetime
from decimal import *
from flowmeter import *
from config import *

#config file is defining KEY and BASE_URL

logging.basicConfig(
	filename='gpioDaemon.log',
	level=logging.DEBUG,
	format='%(asctime)s:%(levelname)s:%(message)s')

DEBUG=True

logging.info('Running gpio-daemon')
logging.info('DEBUG %s', DEBUG)

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)
# Set the correct pin
GPIO.setup(17 , GPIO.IN)
logging.info('Setup GPIO pin as input')

logging.info('Setup Flowmeter')
#pulling from flowmeter.py
fm = FlowMeter('', ['beer'])

#Class GpioDaemon:

def sensorCallback1(channel):
	# Called if sensor output goes LOW
	timestamp = time.time()
	stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
	currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
	#print "Sensor LOW " + stamp
	if fm.enabled == True:
		fm.update(currentTime)
		logging.info(fm.lastClick)

def pourDrinkEvent(clicks):
	#drink is being poured
	#need to wait for it to finish
	logging.info('in drink loop')
	logging.info('initial clicks %s', clicks)
	logging.info('initial fmclicks %s', fm.clicks)
	time.sleep(3)
	logging.info('after sleep clicks %s', clicks)
	logging.info('after sleep fmclicks %s', fm.clicks)
	
	if(fm.clicks <= 3):
		#ghost pour
		logging.info('ghost pour, %s', fm.clicks)
		fm.clear()
	
	elif(fm.clicks == clicks and fm.clicks > 3):				
		#not pouring?
		logging.info(fm.clicks)
		reportDrinkEvent(fm.clicks)
	else:
		#return to loop
		logging.info('in pourDrinkEvent else condition')
		pourDrinkEvent(fm.clicks)

def reportDrinkEvent(clicks):
	#the server should calculate oz from ticks but I was getting bad readings from it.
	mlVolume = clicks*2.25
	myDrink = {'api_key': KEY, 'ticks': clicks, 'volume_ml': mlVolume}
	p = requests.post(BASE_URL+'taps/fake.1', data=myDrink)
	#drink reported, resetting indictator
	fm.clear()
	data = p.json()
	logging.info(data)
	return data

def pourGet():
	return fm.getFormattedTotalPour()

def pourReset():
	fm.clear()

def stillAlive():
	Timer(600, stillAlive).start()
	logging.info('still alive')

def main():
	#initial build out
	GPIO.add_event_detect(17, GPIO.FALLING, callback=sensorCallback1)
	stillAlive()
	try:
		while True:
			time.sleep(1)
			#logging.info('in sleep loop')
			#push this off to definition
			if(fm.clicks > 0):
				pourDrinkEvent(fm.clicks)
	except KeyboardInterrupt:
		GPIO.cleanup()			
if __name__=="__main__":
	main()

#old testing code, includes adding controller

#syntax for adding controllers
#payload_add_controller = {'api_key': KEY, 'name': 'fake', 'serial_number': '0101', 'model_name':'fake-pi' }
#add_controller = requests.post(BASE_URL+'controllers', data=payload5)

#test_drink = {'api_key': KEY, 'ticks': '100'}
#test_drink2 = {'api_key': KEY, 'ticks': fm.clicks}
#a = requests.post(BASE_URL+'taps/fake.1', data=test_drink)
#b = requests.post(BASE_URL+'taps/fake.1', data=test_drink2)

#taps = requests.get('BASE_URL+'taps')
