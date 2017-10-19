from aiohttp import web
import socketio
import json

import time
import sqlite3

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

conn = sqlite3.connect('test.sq3', check_same_thread=False)
conn.row_factory = sqlite3.Row

def getAll():
    c = conn.cursor()
    c.execute("SELECT * FROM weather_data WHERE time >= {}".format(int(time.time()) - (60 * 60 * 24)))

    res = c.fetchall()

    result = {
                "temperature" : [],
                "humidity" : [],
                "pressure" : []
            }

    for item in res:
        for i in ["temperature", "humidity", "pressure"]:
            result[i].append([item['time'] * 1000, item[i]])

    return result


@sio.on('connect', namespace='/ws')
async def connect(sid, environ):
    #publish_data(1000, {"temperature" : 0, "humidity" : 0, "pressure" : 0})
    await sio.emit('init', json.dumps(getAll()), namespace="/ws")

@sio.on('disconnect', namespace='/ws')
def disconnect(sid):
    print('disconnect ', sid)

def publish_data(ts, data):
    log.info("Publishing new data")
    sio.send(json.dumps({
        "temperature" : [ts * 1000, data['temperature']],
        "humidity" : [ts * 1000, data['humidity']],
        "pressure" : [ts * 1000, data['pressure']],
    }), namespace="/ws")

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
