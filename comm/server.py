"""
Server functions that allow us to communicate over sockets to control devices

author: Teddy Tortorici
"""

import time
import socket
import get
import comm.gpib as gpib
import comm.fake_gpib as fake


class GpibServer:

    shutdown_command = b"shutdown"

    """ADDRESSES"""
    addr_bridge = {"AH": 28, "HP": 5}
    addr_ls = {331: 13, 340: 12}

    def __init__(self, bridge_type: str = "AH", ls_model: int = 331, silent: bool = True):
        self.host_port = ("localhost", get.port)
        self.running = False
        self.silent = silent

        """create objects for devices"""
        if bridge_type == "FAKE":
            self.bridge = fake.Bridge()
            self.ls = fake.Lakeshore()
        else:
            self.bridge = gpib.Device(GpibServer.addr_bridge[bridge_type])
            self.ls = gpib.Device(GpibServer.addr_ls[ls_model])

    def handle(self, message_to_parse: str) -> str:
        """Parse a message of the format
        [Instrument ID]::[command]::[optional message]"""
        msg_list = message_to_parse.upper().split('::')
        dev_id = msg_list[0]
        command = msg_list[1]
        try:
            message = msg_list[2]
        except IndexError:
            message = ""

        """SELECT DEVICE (instrument)"""
        if dev_id == "LS":
            instrument = self.ls
            dev_name = "Lakeshore Temperature Controller"
        elif dev_id == "AH" or dev_id == "HP":
            instrument = self.bridge
            dev_name = f"{dev_id} Capacitance Bridge"
        else:
            instrument = None
            dev_name = "Failed to find an instument"
        if not self.silent:
            print(f"Connecting to: {dev_name}")

        if instrument:
            if command[0] == "W":
                if not self.silent:
                    print(f'Writing "{message}" to {dev_id}')
                instrument.write(message)
                msgout = 'empty'
            elif command[0] == "Q":
                if not self.silent:
                    print(f'Querying {dev_id} with "{message}"')
                msgout = instrument.query(message)
            elif command[0] == "R":
                if not self.silent:
                    print(f'Reading from {dev_id}')
                msgout = instrument.read()
        else:
            msgout = f'Did not give a valid device id: {dev_id}'
        return msgout

    def run(self):
        """Establishes a socket server which takes and handles commands"""
        self.running = True
        # open a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.host_port)

            # confirm the socket is bound
            print(f"Socket bound to port: {self.host_port[1]}")

            # put the socket into listening mode
            s.listen()

            # loop until a client requests the server shutdown
            while self.running:
                # establish a connection with a client
                conn, addr = s.accept()
                with conn:
                    if not self.silent:
                        print(f"Connected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                    while True:
                        msg_client = conn.recv(1024)
                        if not self.silent:
                            print(repr(msg_client))
                        if not msg_client:
                            break
                        elif msg_client == GpibServer.shutdown_command:
                            print('Received shutdown command')
                            self.running = False
                            break
                        else:
                            msg_client = msg_client.decode()
                            if not self.silent:
                                print(f'Received message: {msg_client}')
                            msg_server = self.handle(msg_client)
                            conn.sendall(msg_server.encode())


def server_echo_rev(host: str = "localhost", port: int = get.port):
    """Establishes a socket server which echos back at the the client witht the message reversed
    If it receives 'ping', will respond 'gnip'"""
    # set the while loop to begin running
    running = True

    # open a new socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))

        # confirm the socket is bound
        print(f"Socket bound to port: {port}")

        # put the socket into listening mode
        s.listen()

        # loop until a client requests the server shutdown
        while running:
            # establish a connetion with a client
            conn, addr = s.accept()
            with conn:
                print(f"Connected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                while True:
                    msg_client = conn.recv(1024)
                    print(repr(msg_client))
                    if not msg_client:
                        break
                    elif msg_client == b"shutdown":
                        running = False
                        break
                    else:
                        print(f'Received message: {msg_client.decode()}')
                        msg_server = msg_client.decode()[::-1]
                        conn.sendall(msg_server.encode())


if __name__ == "__main__":
    # server_echo_rev()
    server = GpibServer()
    server.run()
