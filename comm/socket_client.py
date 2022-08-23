"""
Tools for communicating with the server with sockets

@author: Teddy Tortorici
"""

import socket
import get


def send(msg: str, host: str = "localhost", port: int = 62538) -> str:
    if msg:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # connect to server
            s.connect((host, port))

            # send message to server
            s.send(msg.encode())

            # get response from the server
            msg_back = s.recv(1024)
        # print(msg_back)
        return msg_back.decode()
    else:
        return "did not send anything"


class Device:
    """This class is meant to be inherited by classes dedicated to specific devices"""

    def __init__(self, dev_id):
        self.dev_id = dev_id
        self.host = "localhost"
        self.port = get.port

    def query(self, msg):
        return self.send(f"{self.dev_id}::Q::{msg}")

    def write(self, msg):
        self.send(f"{self.dev_id}::W::{msg}")
        return "empty"

    def read(self):
        return self.send(f"{self.dev_id}::R")

    def get_id(self):
        return self.query('*IDN?')

    def reset(self):
        self.write('*RST')
        return "reset"

    def send(self, msg):
        return send(msg, self.host, self.port)


if __name__ == "__main__":
    response = send('test')
    print(response)
