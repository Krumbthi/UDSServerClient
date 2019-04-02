import socket
import sys
import json
import logging
import time


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
Logger = logging.getLogger(__name__)


def main():
    counter = 0
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
    message = dict()

    try:
        # Send data
        message['a'] = "testa"
        message['b'] = "testb"
        message['c'] = "testc"

        while counter <= 10:
            Logger.debug("sending \"%s\"" % message)
            sock.sendall(json.dumps(message).encode("utf-8"))

            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(4096)
                amount_received += len(data)
                Logger.debug("received \"%s\"" % data)
                counter += 1

            time.sleep(2)

    finally:
        Logger.debug('closing socket')
        sock.close()


if __name__ == "__main__":
    main()