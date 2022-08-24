"""
Server functions that allow us to communicate over sockets to control devices

author: Teddy Tortorici
"""

import time
import socket
import get
# import gpib
import fake_gpib_devices as gpib    # delete this for real implementation


class GpibServer:

    shutdown_command = b"shutdown"

    def __init__(self, host: str = "localhost", port: int = get.port, do_print=True):
        self.host_port = (host, port)
        self.running = False
        self.do_print = do_print

        """create objects for devices"""
        # self.lakeshore = gpib.Device(get.gpib_address["LS"])
        # self.voltage_supply = gpib.Device(get.gpib_address["VS"])
        self.lakeshore = gpib.LakeShore(0)
        self.voltage_supply = gpib.VoltageSupply(0)
        self.photon_counter = gpib.PhotonCounter(0)

        """Add any set up commands you want to have done once the server starts running
        ie, you may want to set certain settings by default when the system starts up"""
        # Put start up commands to devices here

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

        """MUST EDIT THE FOLLOWING LINES TO MATCH THE DEVICES YOU ARE USING"""
        if dev_id == "LS":
            instrument = self.lakeshore
            dev_name = "Fake Lakeshore Temperature Controller"
        elif dev_id == "VS":
            instrument = self.voltage_supply
            dev_name = "Fake Voltage Supply"
        elif dev_id == "PC":
            instrument = self.photon_counter
            dev_name = "Fake Photon Counter"
        else:
            instrument = None
            dev_name = "Failed to find an instument"
        if self.do_print:
            print(f"Connecting to: {dev_name}")

        if instrument:
            if command[0] == "W":
                if self.do_print:
                    print(f'Writing "{message}" to {dev_id}')
                instrument.write(message)
                msgout = 'empty'
            elif command[0] == "Q":
                if self.do_print:
                    print(f'Querying {dev_id} with "{message}"')
                msgout = instrument.query(message)
            elif command[0] == "R":
                if self.do_print:
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
                    if self.do_print:
                        print(f"Connected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                    while True:
                        msg_client = conn.recv(1024)
                        if self.do_print:
                            print(repr(msg_client))
                        if not msg_client:
                            break
                        elif msg_client == GpibServer.shutdown_command:
                            print('Received shutdown command')
                            self.running = False
                            break
                        else:
                            msg_client = msg_client.decode()
                            if self.do_print:
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
