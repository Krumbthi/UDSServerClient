import decimal
import json
import socket
import os
import logging

logging.basicConfig(format='%(asctime)s %(name)s %(message)s', level=logging.DEBUG)
Logger = logging.getLogger(__name__)


class StationServer:

    def __init__(self):
        self.Logger = logging.getLogger("StationServer")
        self.Logger.debug("Init StationServer")

        self.serverStack = dict()
        self.errorStack = []

        if 'info' not in self.serverStack:
            self.serverStack['info'] = dict()

        if 'type' not in self.serverStack['info']:
            self.serverStack['info']['type'] = 'standby'

        if 'liveMeasurement' not in self.serverStack:
            self.serverStack['liveMeasurement'] = []

    def getLiveData(self, cMessage):
        self.Logger.debug("get LiveData cMessage %s" % cMessage)

    def dataAnalyse(self, cMessage):
        cMessage['a'] = 'resA'
        self.Logger.debug("dataAnalyse cMessage %s" % cMessage)
        return cMessage


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class MyTCPHandler:
    def __init__(self):
        self.cMessage = dict()
        self.stS = StationServer()
        self.Logger = logging.getLogger("MyTCPHandler")
        self.Logger.debug("MyTCPHandler")

    def handle(self, request):
        cMessage = json.loads(request.strip())
        self.Logger.debug(type(cMessage))

        calcData = self.stS.dataAnalyse(cMessage)

        jsd = json.dumps(calcData, cls=DecimalEncoder).encode("utf-8")
        #self.request.send(jsd)
        return jsd


class MyServer:
    def __init__(self, serverAddr):
        Logger.debug("MyTCPServer init")
        # Create a UDS socket
        self.Sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the port
        Logger.debug("starting up on %s" % serverAddr)
        self.Sock.bind(serverAddr)

        # Listen for incoming connections
        self.Sock.listen(1)

    def serveForever(self):
        sockHandler = MyTCPHandler()

        while True:
            # Wait for a connection
            Logger.debug('waiting for a connection')
            connection, client_address = self.Sock.accept()
            try:
                Logger.debug('connection from {}'.format(client_address))

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(4096)
                    Logger.debug("received \"{}\"".format(data))
                    if data:
                        req = sockHandler.handle(data.decode('utf-8'))
                        connection.sendall(req)
                    else:
                        Logger.debug("no more data from {}".format(client_address))
                        break

            finally:
                # Clean up the connection
                connection.close()


if __name__ == "__main__":
    server_address = './uds_socket'

    # Make sure the socket does not already exist
    try:
        os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise

    server = MyServer(server_address)
    server.serveForever()
