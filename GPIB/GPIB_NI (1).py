# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 14:31:15 2017

@author: Teddy Tortorici
"""

import visa


RQS = (1 << 11)
SRQ = (1 << 12)
TIMO = (1 << 14)


class GPIB(object):
    def __init__(self, addr, serialport=''):
        """Takes the address of the instrument you want to talk to and the 'dev/...' location of the serial port"""
        self.addr = addr
        self.serialport = serialport
        self.rm = visa.ResourceManager()
        self.dev = self.rm.open_resource('GPIB0::%d::INSTR' % self.addr)
    
    def query(self, msg):
        return self.dev.query(msg)
    
    def write(self, msg):
        return self.dev.query(msg)
        
    def write2(self, msg):
        return self.dev.query(msg)
        
    def write3(self, msg):
        self.dev.write(msg)
        
    def read(self):
        self.dev.read()
        
    def read2(self, length=512):
        self.dev.read()
        
    def dev_id(self):
        return self.query('*IDN?')
        
        


if __name__ == "__main__":
    ls = Device(12)