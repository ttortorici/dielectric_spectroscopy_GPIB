import serial
import time

class GPIB():
    def __init__(self, addr, port):
        self.port = port
        self.addr = addr


    def close(self):
        """Close communication"""
        self.ser.close()


    def open(self):
        """Open communication"""
        try:
            self.ser = serial.Serial(self.port, 9600, timeout=0.5)
            time.sleep(0.01)
            self.ser.write('++mode 1\n')
            time.sleep(0.01)
            self.ser.write('++auto 0\n')
            time.sleep(0.01)
            #self.ser.write('++eos 0\n')
            #time.sleep(0.01)
            self.ser.write('++read eoi\n')
            time.sleep(0.01)
            self.ser.write('++addr %d\n' % self.addr)
        except serial.SerialException, e:
            print e
            self.close()
        except KeyboardInterrupt, e:
            print e
            self.close()


    def read(self):
        msgout = ''
        try:
            while 1:
                msg = self.ser.read(1000)
                if len(msg) > 0:
                    msgout += msg
                else:
                    break
        except serial.SerialException, e:
            print e
        except KeyboardInterrupt, e:
            print e
        return msgout


    def write(self, msg):
        temp = self.write2(msg)
        msgout = self.write2(msg)
        return msgout


    def write2(self, msg):
        self.open()
        self.ser.write(msg + '\n')
        time.sleep(0.1)
        msgout = self.read()
        self.close()
        return msgout


class Lakeshore(GPIB):
    def write(self, msg):
        for ii in xrange(3):
            bullshit = self.write2(msg)
        return self.write2(msg)


if __name__ == "__main__":
    ls = GPIB(12, '/dev/tty.usbserial-PX9HMPBU')