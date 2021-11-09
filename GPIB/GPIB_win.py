# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 14:31:15 2017

@author: Teddy Tortorici
"""

import pyvisa
import numpy as np

RQS = (1 << 11)
SRQ = (1 << 12)
TIMO = (1 << 14)


class GPIB(object):
    def __init__(self, addr, serialport=''):
        """Takes the address of the instrument you want to talk to and the 'dev/...' location of the serial port"""
        self.addr = addr
        self.serialport = serialport
        self.rm = pyvisa.ResourceManager()
        if addr == 5:
            """addr 5 is for HP4275A"""
            self.dev = self.rm.open_resource('GPIB0::{}::INSTR'.format(self.addr),
                                             read_termination='\r\n', delay=2)
        else:
            self.dev = self.rm.open_resource('GPIB0::{}::INSTR'.format(self.addr), delay=2)
    
    def query(self, msg):
        try:
            return self.dev.query(msg)
        except pyvisa.errors.VisaIOError:
            return 'timed out'

    def query_ascii(self, msg, sep=',', conv='f'):
        try:
            return self.dev.query_ascii_values(msg, container=np.array, separator=sep, converter=conv)
        except pyvisa.errors.VisaIOError:
            return 'timed out'

    def write(self, msg):
        self.dev.write(msg)
        
    def read(self):
        try:
            return self.dev.read()
        except pyvisa.errors.VisaIOError:
            return 'timed out'
        
    def dev_id(self):
        return self.query('*IDN?')


if __name__ == "__main__":
    ls = GPIB(12)
