"""
MQTT Message Holder

This class manages all incoming messages regarding the PBS job info

Author:
    Petr Stehlik <xstehl14@stud.fit.vutbr.cz> @ 2017/07
"""

import paho.mqtt.client as mqtt
import logging, json, copy
import time

class Holder():

    # Callback function on what to do with the message before storing it in database
    on_receive = None

    # Database dictionary
    # Records are organized by the job ID and received message
    db = dict()

    db_fail = dict()

    finished = dict()

    def __init__(self,
            mqtt_broker,
            mqtt_port,
            mqtt_topics):
        """
        drop_job_arrays The PBS hook sends job arrays where job ID is in format xxxxxxx[xxxx].io01
        """
        self.log = logging.getLogger(__name__)

        self.broker = mqtt_broker
        self.port = mqtt_port
        self.topics = [(str(topic), 0) for topic in mqtt_topics]

        self.db = dict()
        self.db_fail = dict()

        self.client = mqtt.Client()

        # Register methods for connection and message receiving
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.on_receive = self.default_on_receive

        self.on_end = self.default_on_end
        self.on_fail = self.default_on_fail

        self.client.connect(mqtt_broker, self.port, 60)

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
        """
        Take action on received messages
        Currently parsed actions:
            temperature
            humidity
            pressure
        """
        self.log.info("Received message '%s': %s " % (msg.topic, msg.payload))

        topic = str(msg.topic).split('/')

        try:
            payload = str(msg.payload).split(';')
        except Exception as e:
            self.log.error("Failed to load JSON payload. Reason: %s" % str(e))
            return

        timestamp = payload[0]
        value = payload[1]
        sensor = topic[-1]

        self.log.info("Time: %s, Sensor: %s, Value: %s" % (timestamp, value, sensor))
        if timestamp in self.db:
            if sensor in self.db:
                self.log.warning("Value %s for time %s already exists" % (sensor, timestamp))
            self.db[timestamp][sensor] = value
        else:
            self.db[timestamp] = {
                    sensor : value
                    }

        self.check_record(timestamp)

    def check_record(self, timestamp):
        topics = [(topic[0]).split('/')[-1] for topic in self.topics]
        if all(topic in self.db[timestamp] for topic in topics):
            # We can store given record in a database
            self.on_end(timestamp, self.db[timestamp])
            del self.db[timestamp]

    def check_timeout(self):
        """Check timeout in all active records
        The timeout time is taken as ctime + req_time and compared to current unix timestamp
        If current timestamp is smaller, the job is moved to failed db
        """
        for jobid in self.db.copy():
            timeout = self.db[jobid]['runjob'][0]['ctime'] + self.db[jobid]['runjob'][0]['req_time']
            now = int(time.time())

            if timeout < now:
                self.db_fail[jobid] = copy.deepcopy(self.db[jobid])
                del self.db[jobid]
                self.log.info("TIMEOUT: Moving job %s to fail DB" % jobid)

        self.on_fail(jobid)

    def default_on_receive(self, id, data):
        self.log.warning("No on_receive method defined")

    def default_on_end(self, id, data):
        self.log.warning("No on_end method defined")

    def default_on_fail(self, id, data):
        self.log.warning("No on_fail method defined")



