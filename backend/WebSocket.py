from aiohttp import web
import socketio
import json

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

import logging
logging.basicConfig(level=logging.WARN)
log = logging.getLogger()

@sio.on('connect', namespace='/ws')
async def connect(sid, environ):
    print("connect ", sid)
    await sio.emit('init', json.dumps({'temperature' : [
    [1504869255000, 23.1,],
    [1504868952000, 23.1,],
    [1504868649000, 23.1,],
    [1504868347000, 23.1,],
    [1504868044000, 23.2,],
    [1504867741000, 23.2,],
    [1504867438000, 23.2,],
    [1504867136000, 23.2,],
    [1504866833000, 23.2,],
    [1504866530000, 23.2,],
    [1504866228000, 23.2,],
    [1504865925000, 23.3,],
    [1504865622000, 23.3,],
    [1504865319000, 23.3,],
    [1504865017000, 23.3,],
    [1504864714000, 23.3,],
    [1504864411000, 23.4,],
    [1504864108000, 23.4,],
    [1504863806000, 23.4,],
    [1504863503000, 23.4,]
]}), namespace="/ws")

@sio.on('init-1', namespace='/ws')
async def message1(sid):
    print("message ")
    await sio.emit('init-1', "data", namespace="/ws")

@sio.on('disconnect', namespace='/ws')
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
