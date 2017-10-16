import json
import time
import paho.mqtt.publish as publish

MQTT_TEMP = "fake/home/ws/sensor/temperature"
MQTT_HUM = "fake/home/ws/sensor/humidity"
MQTT_PRES = "fake/home/ws/sensor/pressure"
HOST = "localhost"

if __name__ == "__main__":
    with open('data.json') as d:
        for line in d:
            t = int(time.time())
            data = json.loads(line)
            publish.single(MQTT_TEMP, "{0};{1}".format(t, data["temperature"]), hostname=HOST)
            publish.single(MQTT_HUM, "{0};{1}".format(t, data["humidity"]), hostname=HOST)
            publish.single(MQTT_PRES, "{0};{1}".format(t, data["pressure"]), hostname=HOST)

            time.sleep(2.0)
