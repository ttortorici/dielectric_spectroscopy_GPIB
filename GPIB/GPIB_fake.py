import sys

RQS = 1<<11
SRQ = 1<<12
TIMO = 1<<14

# create fake GPIB class for testing

class Gpib:
    def __init__(self, addr, serialport=''):
        if type(addr)==str:
            addr = int(addr.strip('dev'))
        self.addr = addr

    def write(self,str):
        print 'write: %s'%str

    def read(self,len=512):
        old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        res = raw_input('trying to read from addr %d: '%self.addr)
        sys.stdout = old_stdout
        return res

    def clear(self):
        print 'clear'

    def rsp(self):
        old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        msg = raw_input('rsp results to send: ')
        sys.stdout = old_stdout
        return int(msg)

    def trigger(self):
        print 'trigger'

    def loc(self):
        print 'loc'

    def close(self):
        self.loc()

    def config(self,*args):
        print 'config',args

    def tmo(self):
        print 'tmo'

    def eos(self):
        print 'eos'
