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
import threading

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

class IRCClient(patterns.Subscriber):

    def __init__(self):
        super().__init__()
        self.nickname= str()
        self.server=NULL
        self._run = True

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        self.add_msg(msg)
        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            self.server.send(f"DISCONNECT".encode('utf-8'))
            raise KeyboardInterrupt

    def add_msg(self, msg):
        if(msg[0:4] == "NICK"):
            message =msg[0:4] + " " + self.nickname +" " + msg[5:] 
            self.server.send(message.encode('utf-8'))
        else:
            self.view.add_msg(self.nickname, msg)
            message = self.nickname + "<:::>" + msg
            self.server.send(message.encode('utf-8'))

    def handle_received_message(self,msg): 
        # split the message to seperate the nickname and the message
        splitted_msg = msg.split("<:::>")
        nickname = splitted_msg[0]
        message = splitted_msg[1]
        # accepts received message only from clients other than itself
        if(nickname != self.nickname):
            self.view.add_msg(str(nickname), message)
    
    def receive_messages(self):
        while True:
            try:
                message = self.server.recv(1024).decode('utf-8')
                if message =="-CLOSE-":
                    self.close()
                if message[0:4] == 'NICK':
                    self.nickname = message[5:]
                    self.view.add_msg("#global", "Welcome " + self.nickname)
                else:
                    self.handle_received_message(message)
            except:
                # close the connection if receive failed
                self.server.close()
                break

    async def run(self, args):
        """
        Driver of your IRC Client
        """ 
        # initialize socket
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((args.server, int(args.port)))
        # set connection in self.server
        self.server = c
         # handle receiving thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def close(self):
        # close connection   
        self.server.close()
        logger.debug(f"Closing IRC Client object")
        pass

def main(args):
    # Pass your arguments where necessary
    client = IRCClient()
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
   

