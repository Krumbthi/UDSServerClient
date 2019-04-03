import decimal
import json
import socket
import os
import sys
from threading import Timer
import logging

# ----------------------------------------------------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s %(name)s %(message)s', level=logging.DEBUG)
Logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------
# Timer Class
# ----------------------------------------------------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------------------------------------------------
# Global timer
# ----------------------------------------------------------------------------------------------------------------------
Scheduler = GlobalTimer(0.5)


# ----------------------------------------------------------------------------------------------------------------------
# Server
# ----------------------------------------------------------------------------------------------------------------------
class Server():
    def __init__(self, serverAddr):
        self.Logger = logging.getLogger("StationServer")
        self.Logger.debug("Init StationServer")
        self.cMessage = {'a': 0, 'b': 0, 'c': 0}
        self.Connection = None

        # Test Timer
        Scheduler.register_callback(self.getLiveData)

        # Create a UDS socket
        self.Sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.Logger.debug("starting up on %s" % serverAddr)
        self.Sock.bind(serverAddr)

        # Listen for incoming connections
        self.Sock.listen(1)

        self.serverStack = dict()
        self.errorStack = []

        if 'info' not in self.serverStack:
            self.serverStack['info'] = dict()

        if 'type' not in self.serverStack['info']:
            self.serverStack['info']['type'] = 'standby'

        if 'liveMeasurement' not in self.serverStack:
            self.serverStack['liveMeasurement'] = []

    def getLiveData(self):
        self.Logger.debug("get LiveData cMessage %s" % self.cMessage)
        self.cMessage['a'] += 1
        self.cMessage['b'] += 1
        self.cMessage['c'] += 1

    def dataAnalyse(self, data):

        self.cMessage['a'] = data['a']
        self.cMessage['b'] = data['b']
        self.cMessage['c'] = data['c']

        self.Logger.debug("dataAnalyse cMessage %s" % self.cMessage)
        self.getLiveData()

        jsd = json.dumps(self.cMessage).encode("utf-8")
        self.Connection.sendall(jsd)

        #return data

    def serveForever(self):
        while True:
            # Wait for a connection
            self.Logger.debug('waiting for a connection')
            self.Connection, client_address = self.Sock.accept()
            try:
                self.Logger.debug('connection from {}'.format(client_address))

                # Receive the data in small chunks and retransmit it
                while True:
                    data = self.Connection.recv(4096)
                    self.Logger.debug("received \"{}\"".format(data))

                    # if data received handle them
                    if data:
                        js_data = json.loads(data.decode('utf-8').strip())
                        #self.dataAnalyse(js_data)
                        #jsd = json.dumps(self.cMessage).encode("utf-8")
                        #connection.sendall(jsd)
                    else:
                        self.Logger.debug("no more data from {}".format(client_address))
                        break

            finally:
                # Clean up the connection
                self.Connection.close()


# ----------------------------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    server_address = './uds_socket'

    # Make sure the socket does not already exist
    try:
        os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise

    server = Server(server_address)
    try:
        server.serveForever()
    except KeyboardInterrupt:
        Scheduler.unregister_callback(server.getLiveData)
    finally:
        Logger.debug("Server died smoothly")

    sys.exit(0)