#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import asyncio
from asyncio.windows_events import NULL
import logging

import patterns
import view

import argparse
import socket
import select

HEADER = 64
PORT = 8080
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

class IRCClient(patterns.Subscriber):

    def __init__(self):
        super().__init__()
        self.username = str()
        self.server=NULL
        self._run = True

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        # Will need to modify this
        self.add_msg(msg)
        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.server.send(send_length)
        self.server.send(message)
        # temp = 
        self.view.add_msg(self.username, self.server.recv(1024).decode(FORMAT))
        # logger.debug(f"+++++++++++++++++++++++++++++ {temp}")

    async def run(self, args):
        """
        Driver of your IRC Client
        """ 
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((args.server, int(args.port)))
        c.setblocking(0)
        self.server = c

        while True:
            # temp = self.server.recv(1024).decode(FORMAT)
            # self.view.add_msg("other ", "temp".encode(FORMAT))
            
            sockets_list = [self.server]
            read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
            for socks in read_sockets:
                print("hehhe")
                if socks == self.server:
                    message = socks.recv(2048)
                    thread = threading.Thread(target= self.view.add_msg(self.username, message))
                    thread.start()
                    logger.debug(f"+++++++++++++++++++++++++++++ {message}")
                else:
                    break
            
   
  
    def close(self):
        # Terminate connection
        self.server.close()
        logger.debug(f"Closing IRC Client object")
        pass



def main(args):
    # Pass your arguments where necessary
    client = IRCClient()
    print("Please Select a username")
    client.username =input(f"username  >")
    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")
        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(args),
                return_exceptions=True,
            )
        try:
            asyncio.run( inner_run() )
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
    client.close()

if __name__ == "__main__":
    # Parse your command line arguments here
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help = "Target server to initiate a connection to.", required = False, default = "")
    parser.add_argument("--port", help = "Target port to use.", required = False, default = "")

    args = parser.parse_args()
    
    main(args)
