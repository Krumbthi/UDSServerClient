import decimal
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

class EchoProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        Logger.debug(data.decode())
        self.transport.write("Hello from server".encode())


async def main_proto():
    serverAddr = '../UDSServerClient/uds_socket'

    loop = asyncio.get_running_loop()
    server = await loop.create_unix_server(EchoProtocol, serverAddr)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main_proto())
