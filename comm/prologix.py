"""
GPIB using a prologix controller

@author: Teddy Tortorici
"""

import os
import serial


class Device:

    comment = "#"

    def __init__(self, address: int, serial_port, baudrate: int = 921600, timeout=0.25, do_print=False):
        if os.name == "nt":
            serial_port = int(serial_port[3:]) - 1
        self.do_print = do_print
        self.address = address

        if not timeout:
            timeout = 2

        self.dev = serial.Serial(serial_port, baudrate=baudrate, timeout=timeout)
        self.write_raw("++mode 1")
        self.write_raw("++ifc")
        self.write_raw("++read_tmo_ms 200")

        version = self.query("++ver")
        print(f"Established connection with Prologix with version: {version}")

    def write_raw(self, message: str, line_end: str = "\n"):
        self.dev.write(f"{message}{line_end}".encode())

    def query(self, message: str) -> str:
        self.write_raw(f"++addr {self.address}")
        if self.do_print:
            print(f"Querying with {message}")
        self.write_raw(message)

        while True:
            print("trying")
            message_back = self.dev.readlines()
            if message_back:
                if self.do_print:
                    print("Got response")
                break
        return message_back[0].decode().rstrip("\r\n")

    def read(self) -> str:
        self.write_raw(f"++addr {self.address}")
        self.write_raw("++read")
        while True:
            message_back = self.dev.readlines()
            if message_back:
                if self.do_print:
                    print("Got response")
                break
        return message_back.rstrip("\n\r")

    def write(self, message):
        self.write_raw(f"++addr {self.address}")
        self.write_raw(message)

    def get_id(self):
        return self.query("*IDN?")


if __name__ == "__main__":
    ls = Device(13, "/dev/ttyUSB0", do_print=True)
    print(ls.query("KRDG? A"))