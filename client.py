import socket
import sys
import json
import logging
import time
import asyncio

# ----------------------------------------------------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
Logger = logging.getLogger(__name__)

STABLE = 1
SERVERADDRESS = './uds_socket'

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


async def handle_recv(message, loop):
    reader, writer = await asyncio.open_unix_connection(SERVERADDRESS, loop=loop)
    data = await reader.read(4096)
    Logger.debug('Received: %r' % data.decode())



# ----------------------------------------------------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------------------------------------------------
def main():
    counter = 0
    message = dict()
    running = True

    # Send data
    message['data'] = 0
    message['state'] = 'running'

    if STABLE:
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening

        Logger.debug("connecting to %s" % SERVERADDRESS)

        try:
            sock.connect(SERVERADDRESS)
        except socket.error as msg:
            Logger.debug(msg)
            sys.exit(1)

        try:
            sock.sendall(json.dumps(message).encode("utf-8"))
        except BrokenPipeError as err:
            Logger.debug(err)
        #finally:


        while running:
            data = sock.recv(4096)
            #    amount_received += len(data)

            if len(data) > 0:
                Logger.debug("received \"%s\"" % data)
                # message.update(dispatch_data(data))
                d = json.loads(data.decode('UTF-8'))
                message['data'] = d['data']
                counter += 1
                if counter == 20:
                    message['state'] = 'stopped'
                    sock.sendall(json.dumps(message).encode("utf-8"))
            else:
                Logger.debug("empty Message")
                running = False

        Logger.debug('closing socket')
        sock.close()
        # try:
        #     while counter <= 11:
        #         if counter == 2:
        #             message['state'] = 'running'
        #         elif counter == 10:
        #             message['state'] = 'stopped'
        #         elif counter == 11:
        #             message['state'] = 'kill'
        #
        #         Logger.debug("sending \"%s\"" % message)
        #         #sock.sendall(json.dumps(message).encode("utf-8"))
        #
        #         #amount_received = 0
        #         #amount_expected = len(message)
        #
        #         #while amount_received < amount_expected:
        #         data = sock.recv(4096)
        #         #    amount_received += len(data)
        #
        #         if len(data) > 0:
        #             Logger.debug("received \"%s\"" % data)
        #             #message.update(dispatch_data(data))
        #             d = json.loads(data.decode('UTF-8'))
        #             message['data'] = d['data']
        #             counter += 1
        #         else:
        #             Logger.debug("empty Message")
        #
        #         time.sleep(2)
        # except BrokenPipeError as err:
        #     Logger.debug(err)

    #     finally:
    #         Logger.debug('closing socket')
    #         sock.close()
    # else:
    #     while counter <= 10:
    #         Logger.debug(recvData(message))
    #         counter += 1
    #         time.sleep(2)

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(handle_recv(message, loop))
    # loop.close()

if __name__ == "__main__":
    main()