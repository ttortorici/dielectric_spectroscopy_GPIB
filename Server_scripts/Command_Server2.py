# Echo server program
import socket
import time
import os
import threading
import sys
from contextlib import closing

#-----------------------------------------------------------------------------------------------------------------------

today = time.strftime('%Y.%m.%d')
logFileName = "log - " + today + ".txt"


HOST = 'localhost'                                                          
PORT = 58585                                                         # Reserve a port for your service
BUFFER_SIZE = 1024                                                          
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                       # Create a socket object                                                  # Bind to the port


"""def print_write(text):
    log.write(time.strftime("%H:%M:%S") + "  |  " + text)
    log.write("\n")
    sys.stdout.write(text+'\n')
    print 'psh'"""


#-----------------------------------------------------------------------------------------------------------------------


"""if os.path.isfile(logFileName) is True:
    log = open(logFileName, 'a+')
    print_write("[SERVER] Log for " + today + " already exists.")
    print_write("[SERVER] Starting comms")
else:
    print "[SERVER] Log doesn't exist"
    log = open(logFileName, 'a+')                                           # Create file -> log - %date%.txt
    print_write("[SERVER] Log created")"""


def client_handler(conn):
    while True:
        data = conn.recv(BUFFER_SIZE)
        if data == "Comms Shutdown":
            print "------ REMOTE SHUTDOWN ------"
            conn.close()
            raise SystemExit  
            # this will kill the server (remove the line above if you don't want that)
        else:
             print "[COMMS] " + str(addr) + " says: " + data

try:
    s.bind((HOST, PORT))
    s.listen(5)
    print "listening TCP on {HOST} port {PORT}".format(**vars())
    while True:
        conn, addr = s.accept()
        with closing(conn), closing(conn.makefile('rb')) as file:
            for byte in iter(lambda: file.read(1), b''):
                # print numerical value of the byte as a decimal number
                print ord(byte)
            print "" # received all input from the client, print a newline
except KeyboardInterrupt:
    print('Keyboard interrupt received, exiting.')
finally:
    s.close()
        
log.close()