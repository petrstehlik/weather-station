#!/usr/bin/env python
import sys
import RPi.GPIO as GPIO
import time
import paho.mqtt.publish as publish
import logging

import dht
import bmp
import light
import moisture
from average import average

# CONFIGURATION
MQTT_TEMP = "home/ws/sensor/temperature"
MQTT_HUM = "home/ws/sensor/humidity"
MQTT_PRES = "home/ws/sensor/pressure"
MQTT_LIGHT = "home/ws/sensor/light"
MQTT_MOISTURE = "home/ws/sensor/moisture"
HOST = "10.0.0.32"

# Logger initialization
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# initialize GPIO
#GPIO.setwarnings(False)
#GPIO.cleanup()
#GPIO.setmode(GPIO.BCM)

# Variables
humidity = []
i = 0
time_i = 0

while True:
	"""
	Every 10 seconds read data from DHT11 and every 300 (10 * 30) seconds read data
	from BMP180. This ensures that data from DHT11 will make sense. After reading
	data from BMP180 publish everything via MQTT.
	"""
	args = sys.argv
	delay = 10.0

	if len(args) > 1:
		delay = float(args[1])

	result = dht.read()
	if result.is_valid():
		humidity.append(result.humidity)
		i += 1

	if time_i == 30:
		data = bmp.read()
		data["humidity"] = average(humidity)
		data["light"] = light.read()
		data["moisture"] = moisture.read()
		i = 0
		time_i = 0
		humidity = []
		ts = int(time.time())

		log.debug("Sending MQTT messages")
		publish.single(MQTT_TEMP,"{0};{1}".format(ts, data["temperature"]), hostname=HOST)
		publish.single(MQTT_HUM,"{0};{1}".format(ts, data["humidity"]), hostname=HOST)
		publish.single(MQTT_PRES,"{0};{1}".format(ts, data["pressure"]), hostname=HOST)
		publish.single(MQTT_LIGHT,"{0};{1}".format(ts, data["light"]), hostname=HOST)
		publish.single(MQTT_MOISTURE,"{0};{1}".format(ts, data["moisture"]), hostname=HOST)

	time_i += 1
	time.sleep(delay)
