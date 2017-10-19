import logging
import sqlite3
from aiohttp import web

from Holder import Holder
from WebSocket import getAll, app, publish_data

MQTT_TEMP = "home/ws/sensor/temperature"
MQTT_HUM = "home/ws/sensor/humidity"
MQTT_PRES = "home/ws/sensor/pressure"
HOST = "10.0.0.32"
PORT = 1883

conn = sqlite3.connect('test.sq3', check_same_thread=False)

def store_record(timestamp, data):
    log = logging.getLogger("STORE")

    c = conn.cursor()

    log.info("Should store data")
    print(data)

    statement = "INSERT INTO {} (time, temperature, pressure, humidity) VALUES ("\
            "?, ?, ?, ?)".format("weather_data")

    c.execute(statement, (timestamp, data["temperature"], data["pressure"], data["humidity"]))

    conn.commit()
    c.close()

    publish_data(timestamp, data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS weather_data (" \
            "time INTEGER PRIMARY KEY, "\
            "temperature REAL NOT NULL,"\
            "pressure REAL NOT NULL,"\
            "humidity REAL NOT NULL);")
    conn.commit()
    c.close()

    holder = Holder(HOST, PORT, [MQTT_TEMP, MQTT_HUM, MQTT_PRES])
    holder.on_end = store_record

    web.run_app(app, host='127.0.0.1', port=8080)
