"""
Replay portion of weather station data to MQTT channels

Usage: python replay.py [DELAY]

DELAY:optional [float], default: 2.0    - delay in seconds to wait between each set of timeframe
"""
import json
import time
import paho.mqtt.publish as publish
import sys

MQTT_TEMP = "fake/home/ws/sensor/temperature"
MQTT_HUM = "fake/home/ws/sensor/humidity"
MQTT_PRES = "fake/home/ws/sensor/pressure"
HOST = "localhost"

if __name__ == "__main__":
    # Optionally fetch delay in seconds (float), default value: 2.0
    args = sys.argv
    delay = 2.0

    if len(args) > 1:
        delay = float(args[1])

    with open('data.json') as d:
        for line in d:
            t = int(time.time())
            data = json.loads(line)
            publish.single(MQTT_TEMP, "{0};{1}".format(t, data["temperature"]), hostname=HOST)
            publish.single(MQTT_HUM, "{0};{1}".format(t, data["humidity"]), hostname=HOST)
            publish.single(MQTT_PRES, "{0};{1}".format(t, data["pressure"]), hostname=HOST)

            time.sleep(delay)
