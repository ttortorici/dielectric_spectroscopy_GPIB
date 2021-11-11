import platform
import time
import numpy as np
if platform.system() == 'Windows':
    from GPIB.GPIB_win import GPIB
else:
    from GPIB.GPIB_unix import GPIB


class dev(GPIB):  # inherit basic commands from general_instrument_control.py
    def __init__(self, addr, serialport='', devicename=''):
        """Connect to temperature controller and initialize communication"""
        super(self.__class__, self).__init__(addr, serialport)
        self.devicename = devicename


class fake_bridge():
    def __init__(self):
        self.devicename = 'fake bridge'

    def query(self, msg):
        return self.parse(msg)

    def write(self, msg):
        pass

    def read(self):
        return 'fake bridge should only be queried'

    def dev_id(self):
        return 'This is not a real device'

    def parse(self, msg):
        time.sleep(2)
        if msg == 'SH FR':
            return 'FREQUENCY        400.00 E+00 HZ\n'
        elif msg == 'SH AV':
            return 'AVERAGE         AVEREXP=7\n'
        elif msg == 'Q':
            return 'F= 14.000 E+03 HZ C= 1.{}   E+00 PF L= {:.6f}      E-03 DS V= 1.00    E+00 V\n'.format(
                np.random.randint(960000, 989999),
                np.random.rand()
            )

class fake_lakeshore():
    def __init__(self):
        self.devicename = 'fake lakeshore'

    def query(self, msg):
        return self.parse(msg)

    def write(self, msg):
        pass

    def read(self):
        return 'fake bridge should only be queried'

    def dev_id(self):
        return 'This is not a real device'

    def parse(self, msg):
        time.sleep(0.5)
        if msg == 'PID? 1':
            return '+0080.0,+0020.0,+003.00\r\n'
        elif msg == 'PID? 2':
            return '+0050.0,+0020.0,+000.00\r\n'
        elif msg == 'KRDG? A':
            return '+{:03d}.{:02d}\r\n'.format(np.random.randint(200, 300), np.random.randint(0, 99))
        elif msg == "HTR?":
            return '+{:03d}.{:02d}\r\n'.format(np.random.randint(0, 99), np.random.randint(0, 99))
        elif msg == "SETP? 1":
            return '+{:03d}.{:02d}\r\n'.format(np.random.randint(200, 300), np.random.randint(0, 99))
        elif msg == "RAMPST? 1":
            return '{}\r\n'.format(np.random.randint(0, 1))
