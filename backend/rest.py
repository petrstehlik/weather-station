"""
Author: Petr Stehlik <xstehl14@stud.fit.vutbr.cz>
Author: Matej Vido <xvidom00@stud.fit.vutbr.cz>
"""

from flask import Flask, request
import logging
import sqlite3
import json
import time
import requests
import numpy

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

app = Flask(__name__)

conn = sqlite3.connect('db.sq3', check_same_thread=False)
conn.row_factory = sqlite3.Row

APPID = "c11eabf697cfe8167bb53d3c1a7cbd20"

TREND_VAL_COUNT = 120
TREND_ANGLE = 45
TREND_THRESHOLD = dict()
TREND_THRESHOLD["temperature"] = 0.2
TREND_THRESHOLD["humidity"]    = 2
TREND_THRESHOLD["pressure"]    = 0.2
TREND_THRESHOLD["light"]       = 2
TREND_THRESHOLD["moisture"]    = 0.2

@app.route('/init')
def init():
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data WHERE time >= {}".format(int(time.time()) - (60 * 60 * 12)))

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

def val_correction(val_type, val):
    if val_type == "light":
        val = val / 10.23

    elif val_type == "moisture":
        val = (1023 - val) / 10.23

    elif val_type == "pressure":
            val = val / 100.0

    return val

def get_trends():
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data ORDER BY time DESC LIMIT {}".format(TREND_VAL_COUNT))

    res = c.fetchall()

    result = dict()

    for i in ["temperature", "humidity", "pressure", "light", "moisture"]:
        data = [val_correction(i, x[i]) for x in res]
        x_vals = numpy.arange(0, len(data))
        y_vals = numpy.array(data)
        polyfit_vals = numpy.polyfit(x_vals, y_vals, 1)
        a = polyfit_vals[0]
        diff = len(data) * a
        if diff < 0:
            sign = -1
        else:
            sign = 1
        if abs(diff) >= TREND_THRESHOLD[i]:
            result[i] = sign * TREND_ANGLE
        else:
            result[i] = 0

    return result

@app.route('/latest')
def latest():
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data ORDER BY time DESC LIMIT 1")

    res = c.fetchall()

    result = dict()

    trends = get_trends()

    for i in ["temperature", "humidity", "pressure", "light", "moisture"]:
        val = val_correction(i, res[0][i])

        result[i] = [res[0]['time'] * 1000, val, trends[i]]
    return(json.dumps(result))

@app.route("/weather")
def weather():
    forecast = requests.get("http://api.openweathermap.org/data/2.5/forecast?id=3078610&units=metric&appid={}".format(APPID))
    weather = requests.get("http://api.openweathermap.org/data/2.5/weather?id=3078610&units=metric&appid={}".format(APPID))

    if forecast.status_code == 200 and weather.status_code == 200:
        response = {
                "weather" : weather.json(),
                "forecast" : forecast.json()
            }
        return(json.dumps(response))
    else:
        print(str(r))

    return(json.dumps(forecast.json()), 500)

@app.route("/actuators")
def actuators():
    c = conn.cursor()
    c.execute("SELECT * FROM actuators")
    rows = c.fetchall()

    result = []

    for row in rows:
        rec = dict()
        rec["id"] = row["id"]
        rec["name"] = row["name"]
        rec["type"] = row["type"]
        # Set timestamp for javascript
        rec["timestamp"] = row["timestamp"] * 1000
        if row["state"] == 0:
            rec["active"] = False
        else:
            rec["active"] = True
        if rec["name"] == "heating" or rec["name"] == "plants_watering":
            """
            For heating and plants_watering, the state from database is opposite to its activity.
            If the state is 0 (the value is lower than threshold), heating and plant_watering actuators
            are active.
            """
            rec["active"] = not rec["active"]
        c.execute("SELECT * FROM thresholds WHERE actuator_id = ?", (row["id"],))
        thrs = c.fetchall()
        rec["thresholds"] = []
        for thr in thrs:
            thr_dict = dict()
            thr_dict["id"] = thr["id"]
            thr_dict["name"] = thr["name"]
            thr_dict["value"] = thr["value"]
            rec["thresholds"].append(thr_dict)
        result.append(rec)

    return json.dumps(result)

@app.route("/actuator/<int:actuator_id>", methods=['POST'])
def actuator(actuator_id):
    data = request.get_json()
    c = conn.cursor()

    if data != None:
        for rec in data:
            thr_id = int(rec["id"])
            val = float(rec["value"])
            c.execute("UPDATE thresholds SET value = ? WHERE id == ? AND actuator_id == ?", (val, thr_id, actuator_id))
            try:
                conn.commit()
            except sqlite3.OperationalError as e:
                print(str(e))
                conn.commit()

    c.execute("SELECT * FROM actuators WHERE id = ?", (actuator_id,))
    row = c.fetchone()

    rec = dict()
    rec["id"] = row["id"]
    rec["name"] = row["name"]
    rec["type"] = row["type"]
    # Set timestamp for javascript
    rec["timestamp"] = row["timestamp"] * 1000
    if row["state"] == 0:
        rec["active"] = False
    else:
        rec["active"] = True
    if rec["name"] == "heating" or rec["name"] == "plants_watering":
        """
        For heating and plants_watering, the state from database is opposite to its activity.
        If the state is 0 (the value is lower than threshold), heating and plant_watering actuators
        are active.
        """
        rec["active"] = not rec["active"]
    c.execute("SELECT * FROM thresholds WHERE actuator_id = ?", (actuator_id, ))
    thrs = c.fetchall()
    rec["thresholds"] = []
    for thr in thrs:
        thr_dict = dict()
        thr_dict["id"] = thr["id"]
        thr_dict["name"] = thr["name"]
        thr_dict["value"] = thr["value"]
        rec["thresholds"].append(thr_dict)

    return json.dumps(rec)
