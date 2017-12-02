#!/usr/bin/env python
"""
Author: Petr Stehlik <xstehl14@stud.fit.vutbr.cz>
Author: Matej Vido <xvidom00@stud.fit.vutbr.cz>
"""

import logging
import sqlite3
import time

from Holder import Holder
from rest import app

MQTT_TEMP = "home/ws/sensor/temperature"
MQTT_HUM = "home/ws/sensor/humidity"
MQTT_PRES = "home/ws/sensor/pressure"
MQTT_LIGHT = "home/ws/sensor/light"
MQTT_MOISTURE = "home/ws/sensor/moisture"
HOST = "localhost"
PORT = 1883

conn = sqlite3.connect('db.sq3', check_same_thread=False)

def store_record(timestamp, data):
    log = logging.getLogger("STORE")

    c = conn.cursor()

    log.info("Should store data")
    print(data)

    statement = "INSERT INTO {} (time, temperature, pressure, humidity, light, moisture) VALUES ("\
            "?, ?, ?, ?, ?, ?)".format("weather_data")

    c.execute(statement, (timestamp, data["temperature"], data["pressure"], data["humidity"], data["light"], data["moisture"]))

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
            "type TEXT NOT NULL, "\
            "timestamp INTEGER NOT NULL, "\
            "active INTEGER NOT NULL);")
    c.execute("CREATE TABLE IF NOT EXISTS thresholds ("\
            "id INTEGER PRIMARY KEY, "\
            "name TEXT NOT NULL, "\
            "value REAL NOT NULL, "\
            "actuator_id INTEGER NOT NULL, "\
            "FOREIGN KEY(actuator_id) REFERENCES actuators(id));")
    try:
        log = logging.getLogger("Register actuators")

        s_act = "INSERT INTO actuators (name, type, timestamp, active) VALUES (?, ?, ?, ?)"
        s_thr = "INSERT INTO thresholds (name, value, actuator_id) VALUES (?, ?, ?)"

        c.execute(s_act, ("conditioning", "conditioning", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("conditioning_temperature", 25.0, pkey))
        log.info("Registering conditioning actuator")

        c.execute(s_act, ("heating", "heating", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("heating_temperature", 25.0, pkey))
        log.info("Registering heating actuator")

        c.execute(s_act, ("blinds", "blinds", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("blinds_light", 5.0, pkey))
        log.info("Registering blinds actuator")

        c.execute(s_act, ("plants_watering", "plants_watering", int(time.time()), 0))
        pkey = c.lastrowid
        c.execute(s_thr, ("plants_watering_moisture", 0.5, pkey))
        log.info("Registering plants_watering actuator")
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    c.close()

    holder = Holder(HOST, PORT, [MQTT_TEMP, MQTT_HUM, MQTT_PRES, MQTT_LIGHT, MQTT_MOISTURE])
    holder.on_end = store_record

    app.run(debug=False, port=8080, host='0.0.0.0')
