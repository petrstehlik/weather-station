#!/usr/bin/env python
"""
Author: Petr Stehlik <xstehl14@stud.fit.vutbr.cz>
"""

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import logging
import time

MQTT_ACT_BASE = "home/ws/actuator/"
MQTT_ACT_COND = MQTT_ACT_BASE + "conditioning/state"
MQTT_ACT_HEAT = MQTT_ACT_BASE + "heating/state"
MQTT_ACT_BLINDS = MQTT_ACT_BASE + "blinds/state"
MQTT_ACT_WATER = MQTT_ACT_BASE + "plants_watering/state"

HOST = "localhost"
PORT = 1883

class Act_handler():
    def __init__(self,
            log_name,
            mqtt_broker,
            mqtt_port,
            mqtt_topics):
        self.log = logging.getLogger(log_name)
        # Logger initialization
        logging.basicConfig(level=logging.DEBUG)

        self.broker = mqtt_broker
        self.port = mqtt_port
        self.topics = [(str(topic), 0) for topic in mqtt_topics]
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(mqtt_broker, mqtt_port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        Subscribe to all topics
        """
        result, mid = client.subscribe(self.topics)

        if result == mqtt.MQTT_ERR_SUCCESS:
            self.log.info("Successfully subscribed to all topics")
        else:
            self.log.error("Failed to subscribe to topics")

    def on_message(self, client, userdata, msg):
        self.log.info("Received message '%s': %s" % (msg.topic, msg.payload))

        topic = str(msg.topic).split('/')
        state = int(str(msg.payload.decode("utf-8")))

        del topic[-1]

        topic = "/".join(topic)
        timestamp = int(time.time())

        self.log.info("Sending message '%s': [%s] %s" % (topic, timestamp, state))
        publish.single(topic, str(timestamp) + ";" + str(state), hostname=HOST)

act_handler = Act_handler("FAKE ACTUATORS", HOST, PORT, [MQTT_ACT_COND, MQTT_ACT_HEAT, MQTT_ACT_BLINDS, MQTT_ACT_WATER])

while True:
    time.sleep(1)
