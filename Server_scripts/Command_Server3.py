import socket
import threading
import SocketServer
import time
import sys
sys.path.append('../GPIB')
import LS340
import LabJack
import get


class ThreadedRequestHandlerFactory(object):
    '''
    This class allows us to pass the controller object to the
    threaded server
    '''
    def __init__(self, controller):
        self.controller = controller


    def __call__(self, *args, **kwargs):
        handler = ThreadedTCPRequestHandler(*args, **kwargs)
        handler.controller = self.controller
        return handler


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    '''
    This class is where the work is done. The server spawns a new
    ThreadedTCPRequestHandler for every connection  from a
    client.
    '''

    # The handler routine. This handles the client's request
    def handle(self):
        # First acquire the lock. This ensures only one thread
        # at a time can communicate with the sensors
        global lock
        print 'locking thread'
        lock.acquire()

        # Process and split up the received message
        data = self.request.recv(1024).split('||')
        print 'recieved data:'
        print data
        # cmd = data[0].strip() # command to issue
        # print data
        for con in controller:
            if con.devicename == data[0].upper():    
                if data[1].upper() == 'GETALL':
                    data = con.get_lj_v()
        self.request.sendall(str(data))
        
    def get_lj_v():
        for con in controller:
            if con.devicename == 'LJ':
                data = con.get_voltages_ave()
        return data
        
    def get_all_values(self):
        #data = []

        for con in controller:
            try:
                data = con.get_voltages_ave()
            except:
                print "Error: Failed to acquire data from sensor: " + con.devicename
                pass
        return data
        

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    global lock
    #controller = [LS340.dev(12, get.serialport())]
    print 'go'
    controller = [LabJack.LabJack()]

    # controller = [Lakeshore.Lakeshore("temperature")]
    # This lock makes sure that only one request can be made at time for a reading.
    lock = threading.Lock()
    connectionfactory = ThreadedRequestHandlerFactory(controller)

    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 50326

    server = ThreadedTCPServer((HOST, PORT), connectionfactory)
    ip, port = server.server_address
    print "server opened on port: " + str(port)

    try:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        server.serve_forever()
        # print "Server loop running in thread:", server_thread.name
    except KeyboardInterrupt:
        server.shutdown()  # cleanly shutdown the server
        # for sensor in controller:
        #     sensor.shutdown()  # Cleanly disconnect from each sensor and release them
        sys.exit(0)     # exit the program