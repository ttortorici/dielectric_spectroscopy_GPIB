import time
import platform
import socket
import get
import GPIB.GPIB_universal as GPIB

"""ADDRESSES"""
addr_ah2700 = 28
addr_hp4275 = 5
addr_ls331 = 13
addr_ls340 = 12


if platform.system() == 'Windows':
    win = True
else:
    win = False

if win:
    import GPIB.LabJack as LabJack


class GPIBcomm:
    def __init__(self, bridge, cryo, lj):
        if bridge.lower() == 'ah':
            ah = True
            hp = False
        else:
            ah = False
            hp = True
        if ah:
            self.bridgeAH = GPIB.dev(addr_ah2700, get.serialport(), 'AH2700A')
            self.bridgeAH.dev.timeout = 15000
            self.bridgeAH.write('UN DS')            # imaginary in units of loss tangent
            self.bridgeAH.write('CO ON')            # turn on continuous measurement
            time.sleep(0.01)

            """FORMAT"""
            self.bridgeAH.write('FO NOTAT ENG')     # engineering notation
            self.bridgeAH.write('FO LA ON')         # enable labels to be sent
            self.bridgeAH.write('FO IEE OF')        # disable IEEE-488.2 compatible punctuation when set to ON
            self.bridgeAH.write('FO FW FIX')        # fix field width
            self.bridgeAH.write('UN DS')
            print('imported AH2700')
        else:
            self.bridgeAH = None
        if hp:
            self.bridgeHP = GPIB.dev(addr_hp4275, get.serialport(), 'HP4275A')
            self.bridgeHP.dev.timeout = 25000
            self.bridgeHP.write('A2')           # set to capacitor for dispA
            self.bridgeHP.write('B1')           # set to loss for dispB
            self.bridgeHP.write('C1')           # set to auto circuit mode (C1: auto, C2: series, C3: parallel)
            self.bridgeHP.write('H1')           # turn on high res mode (H0: off, H1: on)
            print('imported HP4275')
        else:
            self.bridgeHP = None
        if cryo == 'desert':
            self.ls = GPIB.dev(addr_ls340, get.serialport(), 'LS340')
            print('imported LS340')
        elif cryo == '40K':
            self.ls = GPIB.dev(addr_ls331, get.serialport(), 'LS331')
            print('imported LS331')
        elif cryo == '4K':
            self.ls = None
        if lj:
            self.lj = LabJack.LabJack()
            print('imported LabJack')
        else:
            self.lj = None

        if not win:
            self.ls.meter.write('++eot_enable')

    def parse(self, msg):
        """msg should be INSTRUMENT_NAME::COMMAND, and if COMMAND is WR or WRITE, then
        INSTRUMENT_NAME::WRITE::MESSAGE_TO_INSTRUMENT"""
        msgL = msg.upper().split('::')
        print(msgL)
        if msgL[0] in ['AH', 'AH2700', 'AH2700A']:
            instrument = self.bridgeAH
            print('will send to AH bridge')
        elif msgL[0] in ['HP', 'HP4275', 'HP4275A']:
            instrument = self.bridgeHP
        elif msgL[0] in ['LS', 'LS340', 'LS331', 'LAKESHORE']:
            instrument = self.ls
        elif msgL[0] in ['LJ', 'LABJACK']:
            instrument = self.lj
        else:
            instrument = None

        if instrument:
            if msgL[1] in ['W', 'WR', 'WRITE']:
                print('writing "{}" to {}'.format(msgL[2], msgL[0]))
                instrument.write(msgL[2])
                msgout = 'empty'
            elif msgL[1] in ['Q', 'QU', 'QUERY']:
                print('querying {} with "{}"'.format(msgL[0], msgL[2]))
                msgout = instrument.query(msgL[2])
            elif msgL[1] in ['R', 'RE', 'READ']:
                msgout = instrument.read()
            elif msgL[1] == 'RFP':
                msgout = instrument.get_front_panel()
        else:
            msgout = 'Failed'
        return msgout



def server_main(gpib_comm):

    host = ""
    port = 62535
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    try:
        while True:
            # establish connection with client
            c, addr = s.accept()

            # lock acquired by client
            print_lock.acquire()
            print('Connected to :', addr[0], ':', addr[1], time.ctime(time.time()))

            # Start a new thread and return its identifier
            start_new_thread(commthread, (c, gpib_comm,))
    except KeyboardInterrupt:
        print('interupted')
    s.close()


if __name__ == "__main__":
    Setup_Window().mainloop()
