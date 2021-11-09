import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QRunnable, Qt, QThreadPool, QObject, pyqtSignal
from start_meas_dialog import StartMeasDialog
import threading
from _thread import *
import client_tools
import socket
import time


print_lock = threading.Lock()


class Server(QObject):

    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.running = True
        self.host = "localhost"
        self.port = 62535
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        print("socket binded to port", self.port)

        # put the socket into listening mode
        self.server.listen(5)
        print("socket is listening")

    def start(self):  # gpib_comm):
        # a forever loop until client wants to exit
        while self.running:
            # establish connection with client
            c, addr = self.server.accept()

            # lock acquired by client
            print_lock.acquire()
            print('Connected to :', addr[0], ':', addr[1], time.ctime(time.time()))

            while True:
                # message received from client
                msg_client = c.recv(1024)
                msg_client = msg_client.decode('ascii')
                if msg_client == "shutdown":
                    print_lock.release()
                    c.close()
                    # server.close()
                    self.running = False
                    break

                elif not msg_client:
                    print('unlock thread')
                    # lock released on exit
                    print_lock.release()
                    c.close()
                    break

                else:
                    msg_out = f"Got: {msg_client}"

                    # send back reversed string to client
                    c.send(msg_out.encode('ascii'))

        self.server.close()



if __name__ == "__main__":
    import client_tools

    t = threading.Thread(target=server_main, args=())
    t.start()

    time.sleep(1)
    while True:
        msg = input('lskjf;aljks: ')
        print(client_tools.send(msg))
