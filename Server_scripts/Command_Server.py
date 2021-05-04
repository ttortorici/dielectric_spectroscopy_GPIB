import socket
import threading
import SocketServer
import time
import sys
sys.path.append('../GPIB')
import AH2700A
import LS340
import LabJack
import get


lock = {'AH': threading.Lock(), 'LS': threading.Lock(), 'LJ': threading.Lock()}


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    #def __init__(self):
    #    super(SocketServer.BaseRequestHandler, self).__init__()
        

    def handle(self):
        global lock
        
        lock.acquire()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        
        msgin = self.data.split('||')
        mm = len(msgin)
        if mm == 1:
            if msgin[0].upper() == 'INIT':
                msgout = self.init()
        elif mm == 2:
            if msgin[0].upper() == 'WRITE':
                msgout = self.write2device(msgin[1])
            else:
                msgout = 'Error: invalid string'
        else:
            msgout = 'Error: invalid string'
        self.request.sendall(msgout)
        lock.release()
        
    def init(self):
        self.dev = {}
        self.dev['AH'] = AH2700A.dev(28)
        self.dev['LS'] = LS340.dev(12)
        self.dev['LJ'] = LabJack.LabJack()
                
        return msgout
                    



if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    
    """try:
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
    time.sleep(2)"""

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()