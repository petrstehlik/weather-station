from flask import Flask
import logging
import sqlite3
import json
import time
import requests

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

app = Flask(__name__)

conn = sqlite3.connect('db.sq3', check_same_thread=False)
conn.row_factory = sqlite3.Row

APPID = "c11eabf697cfe8167bb53d3c1a7cbd20"

@app.route('/init')
def init():
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data WHERE time >= {}".format(int(time.time()) - (60 * 60 * 2)))

    res = c.fetchall()

    result = {
                "temperature" : [],
                "humidity" : [],
                "pressure" : [],
                "light" : [],
                "moisture" : []
            }

    for item in res:
        for i in ["temperature", "humidity", "pressure", "light", "moisture"]:
            val = item[i]
            if i == "light":
                val = val / 10.23

            elif i == "moisture":
                val = (1023 - val) / 10.23

            elif i == "pressure":
                val = val / 100.0

            result[i].append([item['time'] * 1000, val])

    return(json.dumps(result))

@app.route('/latest')
def latest():
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data ORDER BY time DESC LIMIT 1")

    res = c.fetchall()

    result = dict()

    for i in ["temperature", "humidity", "pressure", "light", "moisture"]:
        val = res[0][i]
        if i == "light":
            val = val / 10.23

        elif i == "moisture":
            val = (1023 - val) / 10.23

        elif i == "pressure":
                val = val / 100.0


        result[i] = [res[0]['time'] * 1000, val]

    return(json.dumps(result))

@app.route("/weather")
def weather():
    r = requests.get("http://api.openweathermap.org/data/2.5/forecast?id=3078610&units=metric&appid={}".format(APPID))

    if r.status_code == 200:
        return(json.dumps(r.json()))
    else:
        print(str(r))
