#!/usr/bin/env python
"""
Author: Petr Stehlik <xstehl14@stud.fit.vutbr.cz>
Author: Matej Vido <xvidom00@stud.fit.vutbr.cz>
"""

import logging
import sqlite3
import time
import paho.mqtt.publish as publish

from Holder import Holder
from rest import app, val_correction

MQTT_TEMP = "home/ws/sensor/temperature"
MQTT_HUM = "home/ws/sensor/humidity"
MQTT_PRES = "home/ws/sensor/pressure"
MQTT_LIGHT = "home/ws/sensor/light"
MQTT_MOISTURE = "home/ws/sensor/moisture"

MQTT_ACT_BASE = "home/ws/actuator/"
MQTT_ACT_COND = MQTT_ACT_BASE + "conditioning"
MQTT_ACT_HEAT = MQTT_ACT_BASE + "heating"
MQTT_ACT_BLINDS = MQTT_ACT_BASE + "blinds"
MQTT_ACT_WATER = MQTT_ACT_BASE + "plants_watering"

HOST = "localhost"
PORT = 1883

conn = sqlite3.connect('db.sq3', check_same_thread=False)
conn.row_factory = sqlite3.Row

def store_record(timestamp, data):
    log = logging.getLogger("STORE")

    c = conn.cursor()

    log.info("Should store data")
    log.info(data)

    c.execute("SELECT * FROM actuators");
    rows = c.fetchall();

    for row in rows:
        c.execute("SELECT * FROM thresholds WHERE actuator_id == {}".format(row["id"]))
        data_vals = {k: val_correction(k, float(data[k])) for index, k in enumerate(data)}
        thrs = c.fetchall()
        new_state = 1
        for thr in thrs:
            if data_vals[thr["name"]] < thr["value"]:
                new_state = 0
                break
        log.info("Actuator %s state: %s new_state: %s" % (row["type"], row["state"], new_state))
        if new_state != row["state"]:
            log.info("Sending message '%s': %s " % (MQTT_ACT_BASE + row["type"] + "/state", new_state))
            publish.single(MQTT_ACT_BASE + row["type"] + "/state", str(new_state), hostname=HOST)


    statement = "INSERT INTO {} (time, temperature, pressure, humidity, light, moisture) VALUES ("\
            "?, ?, ?, ?, ?, ?)".format("weather_data")

    c.execute(statement, (timestamp, data["temperature"], data["pressure"], data["humidity"], data["light"], data["moisture"]))

    try:
        conn.commit()
    except sqlite3.OperationalError as e:
        print(str(e))
        conn.commit()
    c.close()

def actuator_on_message(client, userdata, message):
    log = logging.getLogger("ACTUATORS STATUS UPDATE")
    log.info("Received message '%s': %s " % (message.topic, message.payload))
    #TODO actualize state of actutator in database

    topic = str(message.topic).split('/')

    try:
        payload = str(message.payload.decode("utf-8")).split(';')
    except Exception as e:
        log.error("Failed to load JSON payload. Reason: %s" % str(e))
        return

    actuator = topic[-1]
    timestamp = payload[0]
    state = payload[1]

    log.info("Actuator: %s, Timestamp: %s, State: %s" % (actuator, timestamp, state))

    c = conn.cursor()
    c.execute("UPDATE actuators SET timestamp = ?, state = ? WHERE type == ?", (timestamp, state, actuator))
    try:
        conn.commit()
    except sqlite3.OperationalError as e:
        print(str(e))
        conn.commit()
    c.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS weather_data (" \
            "time INTEGER PRIMARY KEY, "\
            "temperature REAL NOT NULL,"\
            "pressure REAL NOT NULL,"\
            "light REAL NOT NULL,"\
            "moisture REAL NOT NULL,"\
            "humidity REAL NOT NULL);")
    c.execute("CREATE TABLE IF NOT EXISTS actuators ("\
            "id INTEGER PRIMARY KEY, "\
            "name TEXT UNIQUE NOT NULL, "\
            "type TEXT UNIQUE NOT NULL, "\
            "timestamp INTEGER NOT NULL, "\
            "state INTEGER NOT NULL);")
    c.execute("CREATE TABLE IF NOT EXISTS thresholds ("\
            "id INTEGER PRIMARY KEY, "\
            "name TEXT NOT NULL, "\
            "value REAL NOT NULL, "\
            "actuator_id INTEGER NOT NULL, "\
            "FOREIGN KEY(actuator_id) REFERENCES actuators(id));")
    try:
        log = logging.getLogger("Register actuators")

        s_act = "INSERT INTO actuators (name, type, timestamp, state) VALUES (?, ?, ?, ?)"
        s_thr = "INSERT INTO thresholds (name, value, actuator_id) VALUES (?, ?, ?)"

        c.execute(s_act, ("Conditioning", "conditioning", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("temperature", 25.0, pkey))
        log.info("Registering conditioning actuator")

        c.execute(s_act, ("Heating", "heating", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("temperature", 18.0, pkey))
        log.info("Registering heating actuator")

        c.execute(s_act, ("Blinds", "blinds", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("light", 5.0, pkey))
        log.info("Registering blinds actuator")

        c.execute(s_act, ("Plant Watering", "plants_watering", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("moisture", 0.5, pkey))
        log.info("Registering plants_watering actuator")
    except sqlite3.IntegrityError:
        pass
    try:
        conn.commit()
    except sqlite3.OperationalError as e:
        print(str(e))
        conn.commit()
    c.close()

    holder = Holder("sensors", HOST, PORT, [MQTT_TEMP, MQTT_HUM, MQTT_PRES, MQTT_LIGHT, MQTT_MOISTURE])
    holder.on_end = store_record

    act_holder = Holder("actuators", HOST, PORT, [MQTT_ACT_COND, MQTT_ACT_HEAT, MQTT_ACT_BLINDS, MQTT_ACT_WATER], actuator_on_message)

    app.run(debug=False, port=8080, host='0.0.0.0')
