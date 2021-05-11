import yaml
import time
try:
    import Tkinter
except ImportError:
    import tkinter as Tkinter
import platform
# from builtins import input
import socket
from _thread import *
import threading
# import os
import sys
sys.path.append('GPIB')
import GPIB
import LabJack
import get


"""ADDRESSES"""
addr_ah2700 = 28
addr_hp4275 = 5
addr_ls331 = 13
addr_ls340 = 12


if sys.version_info.major > 2:
    if sys.version_info.minor < 4:
        from imp import reload
    else:
        from importlib import reload
if platform.system() == 'Windows':
    win = True
else:
    win = False

print_lock = threading.Lock()


class Setup_Window(Tkinter.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    LJ_CHs = 4

    def __init__(self):
        """LOAD PREVIOUS SETTINGS"""
        self.yaml_f = 'server_settings.yml'
        with open(self.yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('Set up GPIB Server')

        """
        create and place labels
        """
        columns = 4

        r = 0

        """TITLE LINE"""
        Tkinter.Label(self, text='This will set up a socket programming server for communicating to GPIB',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                             column=0,
                                                                             columnspan=columns,
                                                                             sticky=Tkinter.W)

        r += 1

        """ANDEEN-HAGERLING"""
        Tkinter.Label(self, text="Andeen-Hagerling bridge being used?",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.ah = preset['ah']
        self.ah_selection = Tkinter.IntVar(self)
        self.ah_selection.set(self.ah)

        Tkinter.Radiobutton(self, text="NO", variable=self.ah_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.ahselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="YES", variable=self.ah_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.ahselect).grid(row=r, column=2)
        self.ahselect()       # prints current selection

        r += 1

        """HEWLETT PACKARD"""
        Tkinter.Label(self, text="Hewlett Packard bridge being used?",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.hp = preset['hp']
        self.hp_selection = Tkinter.IntVar(self)

        self.hp_selection.set(self.hp)

        Tkinter.Radiobutton(self, text="NO", variable=self.hp_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.hpselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="YES", variable=self.hp_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.hpselect).grid(row=r, column=2)
        self.hpselect()       # prints current selection

        r += 1

        """CRYOSTAT"""
        Tkinter.Label(self, text="Cryostat being used?",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.cryo = preset['cryo']
        self.cryo_selection = Tkinter.IntVar(self)
        cryo_setting = {'desert': 0,
                        '40K': 1,
                        '4K': 2}
        self.cryo_selection.set(cryo_setting[self.cryo])

        Tkinter.Radiobutton(self, text="DesertCryo", variable=self.cryo_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=1, columnspan=2)
        Tkinter.Radiobutton(self, text="40 K Cryo", variable=self.cryo_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=3)
        Tkinter.Radiobutton(self, text="4 K Cryo", variable=self.cryo_selection, value=2,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=4)
        self.cryoselect()  # prints current result

        r += 1

        """LABJACK"""
        Tkinter.Label(self, text="LabJack being used?",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.lj = preset['lj']
        self.lj_selection = Tkinter.IntVar(self)

        self.lj_selection.set(self.lj)

        Tkinter.Radiobutton(self, text="NO", variable=self.lj_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.ljselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="YES", variable=self.lj_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.ljselect).grid(row=r, column=2)
        self.ljselect()       # prints current selection

        r += 1

        """SOCKET TO USE"""
        Tkinter.Label(self, text="Socket port number to use:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.sock = preset['sock']
        self.sock_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.sock_entry.grid(row=r, column=3, columnspan=1, sticky=Tkinter.E + Tkinter.W)
        self.sock_entry.insert(0, self.sock)

        r += 1

        """GO BUTTON"""
        Tkinter.Button(self, text="START GPIB SERVER",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.go).grid(row=r, column=columns-2, columnspan=2, sticky=Tkinter.E + Tkinter.W)
        r += 1
        Tkinter.Label(self, text="2021 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.killWindow)

        self.attributes('-topmost', True)

    """
    DEFINITIONS FOR SELECTION TOOL IN GUI
    """

    def ahselect(self):
        self.ah = self.ah_selection.get()

    def hpselect(self):
        self.hp = self.hp_selection.get()

    def cryoselect(self):
        if self.cryo_selection.get() == 0:
            self.cryo = 'desert'
        elif self.cryo_selection.get() == 1:
            self.cryo = '40K'
        elif self.cryo_selection.get() == 2:
            self.cryo = '4K'

    def ljselect(self):
        self.lj = self.lj_selection.get()

    """
    MAIN DEFINITION
    """

    def go(self):
        self.sock = int(self.sock_entry.get())
        presets = {'ah': self.ah,
                   'hp': self.hp,
                   'cryo': self.cryo,
                   'lj': self.lj,
                   'sock': self.sock}

        with open(self.yaml_f, 'w') as f:
            yaml.dump(presets, f, default_flow_style=False)

        self.killWindow()

        gpib = GPIBcomm(self.ah, self.hp, self.cryo, self.lj)

        server_main(gpib)

    def killWindow(self):
        self.destroy()


def start():
    Setup_Window.mainloop()


def commthread(c, gpib_comm):
    while True:
        # message received from client
        msg_client = c.recv(1024)
        if not msg_client:
            print('unlock thread')

            # lock released on exit
            print_lock.release()
            break

        # parse message
        msg_out = gpib_comm.parse(msg_client.decode('ascii'))
        print(msg_out)
        print('got it')

        # send back reversed string to client
        c.send(msg_out.encode('ascii'))

    # connection closed
    c.close()

class GPIBcomm:
    def __init__(self, ah, hp, cryo, lj):
        if ah:
            self.bridgeAH = GPIB.dev(addr_ah2700, get.serialport(), 'AH2700A')
            self.bridgeAH.dev.timeout = 25000
            self.bridgeAH.write('UN DS')            # imaginary in units of loss tangent
            self.bridgeAH.write('CO ON')            # turn on continuous measurement
            time.sleep(0.01)

            """FORMAT"""
            self.bridgeAH.write('FO NOTAT ENG')     # engineering notation
            time.sleep(0.01)
            self.bridgeAH.write('FO LA ON')         # enable labels to be sent
            time.sleep(0.01)
            self.bridgeAH.write('FO IEE OF')        # disable IEEE-488.2 compatible punctuation when set to ON
            time.sleep(0.01)
            self.bridgeAH.write('FO FW FIX')        # fix field width
            print('imported AH2700')
        else:
            self.bridgeAH = None
        if hp:
            self.bridgeHP = GPIB.dev(addr_hp4275, get.serialport(), 'HP4275A')
            self.bridgeHP.dev.timeout = 25000
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
                print('writing {} to {}'.format(msgL[2], msgL[0]))
                instrument.write(msgL[2])
                msgout = 'empty'
            elif msgL[1] in ['Q', 'QU', 'QUERY']:
                print('querying {} with {}'.format(msgL[0], msgL[2]))
                msgout = instrument.query(msgL[2])
            elif msgL[1] in ['GFP', 'GETFRONTPANEL', 'GET_FRONT_PANEL', 'READ']:
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
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(commthread, (c, gpib_comm,))
    s.close()


if __name__ == "__main__":
    Setup_Window().mainloop()