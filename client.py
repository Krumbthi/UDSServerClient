import socket
import sys
import json
import logging
import time
from decimal import Decimal

# ----------------------------------------------------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
Logger = logging.getLogger(__name__)

STABLE = 1

# ----------------------------------------------------------------------------------------------------------------------
# dispatcher
# ----------------------------------------------------------------------------------------------------------------------
def dispatch_data(data):
    js_data = json.loads(data.decode('utf-8').strip())
    js_data['data'] = 1
    js_data['b'] -= 1
    js_data['c'] -= 1
    return js_data


def recvData(message):
    server_address = './uds_socket'
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            jSd = json.dumps(message).encode("utf-8")
            # print("Client to Server %s" % jSd)
            sock.send(jSd)
            receivedData = sock.recv(4069)
            received = json.loads(receivedData)

            if received is None:
                return None

    except socket.error as msg:
        Logger.debug("Server error: {}".format(msg))
        return None

    return received


# ----------------------------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------------------------
def main():
    counter = 0
    message = dict()

    # Send data
    message['data'] = 0
    message['state'] = 'stopped'

    if STABLE:
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = './uds_socket'
        Logger.debug("connecting to %s" % server_address)

        try:
            sock.connect(server_address)
        except socket.error as msg:
            Logger.debug(msg)
            sys.exit(1)

        try:
            while counter <= 11:
                if counter == 2:
                    message['state'] = 'running'
                elif counter == 10:
                    message['state'] = 'stopped'
                elif counter == 11:
                    message['state'] = 'kill'

                Logger.debug("sending \"%s\"" % message)
                sock.sendall(json.dumps(message).encode("utf-8"))

                #amount_received = 0
                #amount_expected = len(message)

                #while amount_received < amount_expected:
                data = sock.recv(4096)
                #    amount_received += len(data)
                
                if len(data) > 0:
                    Logger.debug("received \"%s\"" % data)
                    #message.update(dispatch_data(data))
                    message['data'] = json.loads(data.decode())['data']
                    counter += 1
                else: 
                    Logger.debug("empty Message")

                time.sleep(2)
        except BrokenPipeError as err:
            Logger.debug(err)

        finally:
            Logger.debug('closing socket')
            sock.close()
    else:
        while counter <= 10:
            Logger.debug(recvData(message))
            counter += 1
            time.sleep(2)


if __name__ == "__main__":
    main()