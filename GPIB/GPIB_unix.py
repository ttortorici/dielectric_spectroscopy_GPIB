import serial
import time
import sys
import os.path


RQS = (1 << 11)
SRQ = (1 << 12)
TIMO = (1 << 14)


class GPIB():
    def __init__(self, addr, serialport):
        """Takes the address of the instrument you want to talk to and the 'dev/...' location of the serial port"""
        self.port = serialport
        self.addr = addr

    def clear(self):
        """sends the Selected Device Clear (SDC) message to the currently specified GPIB address
        consult programming manual of the specific instrument for how it responds to this"""
        self.write2('++clr')

    def listen_only(self, on=True):
        """Issues command that configures the GPIB-USB to listen to all traffic on the GPIB bus"""
        self.write2('++lon %s' % str(int(bool(on))))

    def local(self):
        """enables front panel operation at specified address"""
        self.write2('++loc')

    def remote(self):
        """disables front panel operation"""
        self.write2('++llo')

    def trigger(self):
        """issues Group Execute Trigger GPIB command to devices at specified address"""
        self.write2('++trg')

    def close(self):
        """Close communication with instrument"""
        self.ser.close()

    def open(self):
        """Open communication with instrument"""
        try:
            self.ser = serial.Serial(self.port, 9600, timeout=0.5)
            time.sleep(0.01)
            self.ser.write('++mode 1\n')
            time.sleep(0.01)
            self.ser.write('++auto 0\n')
            time.sleep(0.01)
            #self.ser.write('++eos 0\n')
            #time.sleep(0.01)
            #self.ser.write('++read eoi\n')
            time.sleep(0.01)
            self.ser.write('++addr %d\n' % self.addr)
        except serial.SerialException as e:       # usually an error with trying to open the port when in use
            print(e)
            self.close()
        except KeyboardInterrupt as e:            # to allow keyboard interrupt if it gets hung up
            print(e)
            self.close()

    def read2(self, length=512):
        self.open()
        self.ser.write('++read eoi\n')
        self.res = self.ser.read(length)
        self.close()
        return self.res

    def query(self, msg, wait=0):
        self.open()
        self.ser.write('%s\n' % msg)
        time.sleep(wait+0.1)
        self.res = self.read2()
        self.close()
        return self.res

    def rsp(self):
        self.open()
        self.ser.write('++spoll\n')
        try:
            self.spb = int(self.port.read(100).strip())
        except:
            print('Error reading serial poll byte')
        self.close()
        return self.spb

    def read(self):
        """read from instrument"""
        self.open()
        self.ser.write('++read eoi\n')
        self.res = ''
        fail = 0
        try:
            while 1:
                self.res = self.ser.read(1000)
                if len(self.res) > 0:
                    break
                fail += 1
                if fail > 2:
                    break
            self.close
        except serial.SerialException as e:
            print(e)
        except KeyboardInterrupt as e:
            print(e)
        return self.res

    def write3(self, msg):
        self.open()
        self.port.write('%s\n' % msg)
        self.close()

    def write(self, msg):
        """write to instrument and return its response the second time it's queried. Use this for queries"""
        print('writing to device')
        temp = self.write2(msg)
        msgout = self.write2(msg)
        return msgout

    def write2(self, msg):
        """write to instrument and return its response. Use this when response from instrument isn't needed"""
        self.open()
        #print 'opened device'
        self.ser.write(msg + '\n')
        #print 'wrote to device'
        time.sleep(0.1)
        msgout = self.read()
        #print 'read from device'
        self.close()
        return msgout


if __name__ == "__main__":
    ls = GPIB(12, '/dev/tty.usbserial-PX9HMPBU')