"""For use of Lakeshore 340"""
import socket

class Lakeshore:
    def __init__(self):
        """Connect to temperature controller and initialize communication"""
        self.devicename = 'LS340'
        self.ip = ''
        self.port = 1 << 12

    def client(self, message):
        port = self.port
        go = True
        while go:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.ip, port))
                sock.sendall(message)
                response = sock.recv(4096)
                sock.close()
                go = False
            except:
                port += 1
        return response

    def id(self):
        """Get identity of device"""
        return self.client('*IDN?')

    def get_heater(self):
        """Query Heater Output. Returns an output in percent"""
        return float(self.client('HTR?'))

    def get_temp(self, ch, units='K'):
        """Get temperature from specified channel. Pass 'C' for units for Celsius"""
        units = units.upper()[0]
        ch = ch.upper()
        #print ch
        if ch in ['A', 'B']:
            #print '%sRDG? %s' % (units, ch)
            msgout = self.client('%sRDG? %s' % (units, ch))
            return float(msgout)
        else:
            raise IOError('Must give "A" or "B" for ch input')
            return ''

    def reset(self):
        """Reset and clear the Lakeshore"""
        self.client('*RST')

    def set_heater_range(self, heat_range):
        """Configure Heater range. Valid entries 0 - 5."""
        heat_range = abs(heat_range)
        if heat_range <= 5:
            self.client('RANGE %s' % heat_range)
        else:
            raise IOError('Must give range value of 0 - 5')

    def set_PID(self, P, I, D):
        """Configure Control Loop PID Values"""
        self.client('PID %s, %s, %s' % (P, I, D))

    def setpoint(self, value, loop=1):
        """Configure Control loop setpoint.
        loop: specifies which loop to configure.
        value: the value for the setpoint (in whatever units the setpoint is using"""
        self.client('SETP %d, %s' % (loop, str(value)))

if __name__ == '__main__':
    ls = Lakeshore()
    temperature = ls.get_temp('A')
    print temperature