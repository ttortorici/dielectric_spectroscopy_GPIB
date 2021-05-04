# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 14:41:14 2017

@author: Teddy
"""

import Command_Server
import SocketServer

if __name__ == "__main__":
    HOST, PORT = "localhost", 340
    go = True
    # Create the server, binding to localhost on port 9999
    while go:
        try:
            server = SocketServer.TCPServer((HOST, PORT), Command_Server.MyTCPHandler)
            go = False
        except:
            PORT += 1


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()