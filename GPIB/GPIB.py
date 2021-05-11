import platform
if platform.system() == 'Windows':
    from GPIB_win import GPIB
else:
    from GPIB_unix import GPIB

class dev(GPIB): # inherit basic commands from general_instrument_control.py
    def __init__(self, addr, serialport='', devicename=''):
        """Connect to temperature controller and initialize communication"""
        super(self.__class__, self).__init__(addr, serialport)
        self.devicename = devicename
