import socket
import threading
import SocketServer
import time
import sys

#import yaml
sys.path.append('../GPIB')
import AH2700A
import LS340
import LabJack
import get


lock = threading.Lock()
global controller #= []

def init_globals(controller_in):
    global controller
    controller = controller_in


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = True


class ThreadedRequestHandlerFactory(object):
    """Allows the user to pass the controller object to the threaded server"""
    def __init__(self, controller):
        self.controller = controller

    def __call__(self, *args, **kwargs):
        #print 'handler call'
        handler = ThreadedTCPRequestHandler(*args, **kwargs)
        handler.controller = self.controller
        return handler

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    """Server spawns a new ThreadedTCPRequestHandler for every connection from the user"""
    def handle(self):
        """handle a request"""
        global lock

        #print "handling"
        # acquire a lock to avoid simultaneity
        lock.acquire()
        #print "lock acquired"

        # get message and process it
        try:
            msg_recv = self.request.recv(1024).lower()
        except SocketError:
            msg_recv = 'connection reset'
        #cmd = data[0].strip().lower()   # command to issue
        #print cmd

        self.write(msg_recv)

        lock.release()
        return

    def writeRaw(self, msg_in):
        """write directly to a controller"""
        # First find the controller to be written to
        for con in controller:
            #print con.devicename
            msg_out = con.write2(msg_in[2])
            time.sleep(0.1)
            self.request.sendall(msg_out)
        print msg_out
        return msg_out

    def write(self, msg):
        temp = self.writeRaw(msg + '\r\n')
        msgout = self.writeRaw(msg + '\r\n')
        return msgout

    """
    def write(self, msg):
        print 'writing to device'
        temp = self.write2(msg)
        msgout = self.write2(msg)
        return msgout

    def write2(self, msg):

        self.open()
        #print 'opened device'
        self.ser.write(msg + '\n')
        #print 'wrote to device'
        time.sleep(0.1)
        msgout = self.read()
        #print 'read from device'
        self.close()
        return msgout
    """

    def shutdown(self):
        print 'server shutting down...'
        self.server.shutdown()
        self.server.server_close()


if __name__ == "__main__":
    global lock

    HOST, PORT = "", 50326

    #with open('config.yaml') as f:
    #    config = yaml.load(f)
    bridge = AH2700A.dev(28, get.serialport())
    ls = LS340.dev(12, get.serialport())
    try:
        lj = LabJack.LabJack()
    except:
        pass
    deviceType = 'LS340'
    controller = []

    if deviceType == 'AH2700A':
        controller.append(bridge)
    elif deviceType == 'LS340':
        controller.append(ls)
    elif deviceType == 'LabJack':
        controller.append(lj)
    else:
        print "invalid module"
        sys.exit(0)

    lock = threading.Lock()
    connectionfactory = ThreadedRequestHandlerFactory(controller)

    server = ThreadedTCPServer((HOST, PORT), connectionfactory)
    ip, port = server.server_address
    print "server opened on port: " + str(port)

    """connectionfactory = [0] * len(controllers)
    server = [0] *len(controllers)
    for ii, controller in enumerate(controllers):
        connectionfactory[ii] = ThreadedRequestHandlerFactory(controller)
        server[ii] = ThreadedTCPServer((HOST, PORT), connectionfactory)
        ip, port = server[ii].server_address
        print "server opened on port: " + str(port)"""

    try:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        while server_thread.is_alive():
            time.sleep(2)
    except KeyboardInterrupt:
        print 'keyboard interupt'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', PORT))
        s.send('shutdown\n')
        s.close()
        server.shutdown()
    time.sleep(2)