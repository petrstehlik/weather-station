#!/usr/bin/env python
"""
Replay portion of weather station data to MQTT channels

Usage: python replay.py [DELAY]

DELAY:optional [float], default: 2.0    - delay in seconds to wait between each set of timeframe
"""
import json
import time
import paho.mqtt.publish as publish
import sys
import logging

# CONFIGURATION
MQTT_TEMP = "home/ws/sensor/temperature"
MQTT_HUM = "home/ws/sensor/humidity"
MQTT_PRES = "home/ws/sensor/pressure"
MQTT_LIGHT = "home/ws/sensor/light"
MQTT_MOISTURE = "home/ws/sensor/moisture"
HOST = "localhost"

# Logger initialization
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

while True:
    # Optionally fetch delay in seconds (float), default value: 2.0
    args = sys.argv
    delay = 2.0

    if len(args) > 1:
        delay = float(args[1])

    with open('fake-sensors/data.json') as d:
        for line in d:
            data = json.loads(line)
            ts = int(time.time())

            log.debug("Sending MQTT messages")
            publish.single(MQTT_TEMP,"{0};{1}".format(ts, data["temperature"]), hostname=HOST)
            publish.single(MQTT_HUM,"{0};{1}".format(ts, data["humidity"]), hostname=HOST)
            publish.single(MQTT_PRES,"{0};{1}".format(ts, data["pressure"]), hostname=HOST)
            publish.single(MQTT_LIGHT,"{0};{1}".format(ts, data["light"]), hostname=HOST)
            publish.single(MQTT_MOISTURE,"{0};{1}".format(ts, data["moisture"]), hostname=HOST)

            time.sleep(delay)
