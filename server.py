import json
import socket
import os
import sys
from threading import Timer
import logging
import asyncio
import time


# ----------------------------------------------------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s %(name)s %(message)s', level=logging.DEBUG)
Logger = logging.getLogger(__name__)

Running = True

class GlobalTimer(object):
    def __init__(self, interval=1.0):
        self._registered = set()
        self._interval = interval
        self._timer = None
        self._start_timer()

    def register_callback(self, callback):
        self._registered.add(callback)

    def unregister_callback(self, callback):
        self._registered.remove(callback)

    def _start_timer(self):
        self._timer = Timer(self._interval, self._callback)
        self._timer.start()

    def _callback(self):
        for callback in self._registered:
            callback()
        self._start_timer()


Scheduler = GlobalTimer(0.2)

class Server(asyncio.Protocol):
    def __init__(self):
        Scheduler.register_callback(self.doSomething)
        self.Counter = 0
        self.Message = {'data': 0, 'state': 'stopped'}

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        ret = json.loads(data.decode())
        Logger.debug("{}".format(ret))

        if ret['state'] == 'kill':
            Scheduler.unregister_callback(self.doSomething)
            Logger.debug("dying")
            sys.exit(0)

        self.Message['state'] = ret['state']
        self.transport.write(json.dumps(self.Message).encode())

    def doSomething(self):
        if self.Message['state'] == 'running':
            self.Counter += 1
            self.Message['data'] = self.Counter
            Logger.debug(self.Message)


async def main_proto():
    serverAddr = './uds_socket'

    loop = asyncio.get_running_loop()
    server = await loop.create_unix_server(Server, serverAddr)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main_proto())
