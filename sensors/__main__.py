#!/usr/bin/env python
import sys
import RPi.GPIO as GPIO
import time
import paho.mqtt.publish as publish
import logging

import dht
import bmp

# CONFIGURATION
MQTT_TEMP = "home/ws/sensor/temperature"
MQTT_HUM = "home/ws/sensor/humidity"
MQTT_PRES = "home/ws/sensor/pressure"
HOST = "10.0.0.32"

# Logger initialization
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Variables
humidity = 0
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
		humidity += result.humidity
		i += 1

	if time_i == 30:
		data = bmp.read()
		data["humidity"] = humidity/(i)
		i = 0
		time_i = 0
		humidity = 0
		ts = int(time.time())

		log.debug("Sending MQTT messages")
		publish.single(MQTT_TEMP,"{0};{1}".format(ts, data["temperature"]), hostname=HOST)
		publish.single(MQTT_HUM,"{0};{1}".format(ts, data["humidity"]), hostname=HOST)
		publish.single(MQTT_PRES,"{0};{1}".format(ts, data["pressure"]), hostname=HOST)

	time_i += 1
	time.sleep(delay)
