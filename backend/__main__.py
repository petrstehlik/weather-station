import logging
import sqlite3

from Holder import Holder

MQTT_TEMP = "fake/home/ws/sensor/temperature"
MQTT_HUM = "fake/home/ws/sensor/humidity"
MQTT_PRES = "fake/home/ws/sensor/pressure"
HOST = "localhost"
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
    while True:
        pass
