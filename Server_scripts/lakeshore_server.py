import socket
import threading
import SocketServer
import time
import sys
import command_server
import signal
sys.path.append('../GPIB')
import LS340
import get


def signal_handler(signal, frame):
    """After pressing ctrl-C to quit, this function will first run"""
    global ip, port, server
    print '\nkeyboard interupt'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send('shutdown\n')
    s.close()
    server.shutdown()
    print 'quitting'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

HOST, PORT = "", 1 << 12

# with open('config.yaml') as f:
#    config = yaml.load(f)
ls = LS340.dev(12, get.serialport())

controller = [ls]

command_server.init_globals(controller)

connectionfactory = command_server.ThreadedRequestHandlerFactory(controller)
go = True
while go:
    try:
        server = command_server.ThreadedTCPServer((HOST, PORT), connectionfactory)
        go = False
    except SocketServer.socket.error:
        PORT += 1

ip, port = server.server_address
print "server opened on port: " + str(port)

#try:
if 1:
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    while server_thread.is_alive():
        time.sleep(2)
"""except KeyboardInterrupt:
    print 'keyboard interupt'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', PORT))
    s.send('shutdown\n')
    s.close()
    server.shutdown()"""
time.sleep(2)