import platform
if platform.system() == 'Windows':
    win = True
else:
    win = False
if win:
    from GPIB_NI import GPIB
else:
    from GPIB import GPIB

"""Driver for using Lakeshore 331"""

class dev(GPIB): # inherit basic commands from general_instrument_control.py
    def __init__(self, addr, serialport=''):
        """Connect to temperature controller and initialize communication"""
        super(self.__class__, self).__init__(addr, serialport)
        self.devicename = 'LS340'
        #self.addr = addr
        #self.port = serialport

    def id(self):
        """Get identity of device"""
        return self.write('*IDN?')

    def get_heater(self):
        """Query Heater Output. Returns an output in percent"""
        return float(self.write('HTR?'))

    def get_temp(self, ch, units='K'):
        """Get temperature from specified channel. Pass 'C' for units for Celsius"""
        units = units.upper()[0]
        ch = ch.upper()
        if ch in ['A', 'B']:
            msgout = self.write('%sRDG? %s' % (units, ch))
            return float(msgout)
        else:
            raise IOError('Must give "A" or "B" for ch input')
            return ''

    def reset(self):
        """Reset and clear the Lakeshore"""
        self.write3('*RST')

    def set_heater_range(self, heat_range):
        """Configure Heater range. Valid entries 0 - 3 OR 'OFF', 'LOW', 'MED', 'HIGH'."""
        try: heat_range = abs(int(heat_range))
        except TypeError:
            if heat_range[:1].upper() == 'O':
                heat_range = 0
            elif heat_range[:1].upper() == 'L':
                heat_range = 1
            elif heat_range[:1].upper() == 'M':
                heat_range = 2
            elif heat_range[:1].upper() == 'H':
                heat_range = 3
            else:
                heat_range = 4
        if heat_range <= 3:
            self.write3('RANGE %s' % heat_range)
        else:
            raise IOError('Must give range value of 0 - 3 OR "OFF", "LOW", "MED", "HIGH"')

    def set_PID(self, P, I, D, loop=1):
        """Configure Control Loop PID Values"""
        self.write3('PID %d %d, %d, %d' % (loop, P, I, D))

    def setpoint(self, value, loop=1):
        """Configure Control loop setpoint.
        loop: specifies which loop to configure.
        value: the value for the setpoint (in whatever units the setpoint is using"""
        self.write3('SETP %d, %s' % (loop, str(value)))

if __name__ == '__main__':
    import get

    bridge = dev(12, get.serialport())
    temperature = bridge.get_temp('A')
    print temperature