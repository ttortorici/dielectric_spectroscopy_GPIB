import time
import platform
import numpy as np
if platform.system() == 'Windows':
    win = True
else:
    win = False
if win:
    from GPIB_NI import GPIB
else:
    from GPIB import GPIB
import sys
sys.path.append('../other')

"""Driver for using HP 4275A Capactiance Bridge"""
# Refer to Section 3 of HP 4275 operation Manual

class dev(GPIB):
    def __init__(self, addr, serialport=''):
        """Connect to Cap Bridge and initialize communications"""
        super(self.__class__, self).__init__(addr, serialport)
        self.devicename = 'HP4275A'
        self.dev.timeout = 25000
        self.addr = addr
        """self.write3('A2')
        time.sleep(0.01)
        self.write3('B1')
        time.sleep(0.01)
        self.write3('C1')
        time.sleep(0.01)
        self.write3('D0')
        time.sleep(0.01)
        self.write3('H1')
        time.sleep(0.01)
        self.write3('R31')
        time.sleep(0.01)
        self.write3('M3')
        print 'HP fully connected'"""
        
        

    def clear(self):
        """Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device."""
        self.write2('DC1')
        print 'Cleared'

    def getCL(self, msg):
        self.query('A2')
        time.sleep(0.02)
        self.query('B1')
        time.sleep(0.02)
        rawmsg = self.query(msg)
        for ii, char in enumerate(rawmsg):
            if char == '+' or char == '-':
                start1 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispA = float(rawmsg[start1:len(rawmsg)-count])
                go = False
            except ValueError:
                count += 1
        rawmsg2 = rawmsg[len(rawmsg)-count:]
        for ii, char in enumerate(rawmsg2):
            if char == '+' or char == '-':
                start2 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispB = float(rawmsg2[start2:len(rawmsg2)-count])
                go = False
            except ValueError:
                count += 1
        return dispA*1e12, dispB

    def get_dispA(self, value='C'):
        """values: 'C' - capacitance, 'L' - inductance, 'R' - resistance, 'Z' - impedence"""
        dispA_dict = {'L': 'A1', 'C': 'A2', 'R': 'A3', 'Z': 'A4'}
        rawmsg = self.query(dispA_dict[value])
        return rawmsg
    
    def get_RC(self, msg):
        self.query('A3')
        time.sleep(0.02)
        self.query('B2')
        time.sleep(0.02)
        #self.query('B2')
        #time.sleep(0.02)
        rawmsg = self.query(msg)
        for ii, char in enumerate(rawmsg):
            if char == '+' or char == '-':
                start1 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispA = float(rawmsg[start1:len(rawmsg)-count])
                go = False
            except ValueError:
                count += 1
        rawmsg2 = rawmsg[len(rawmsg)-count:]
        for ii, char in enumerate(rawmsg2):
            if char == '+' or char == '-':
                start2 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispB =  float(rawmsg2[start2:len(rawmsg2)-count])
                go = False
            except ValueError:
                count += 1
        return dispA, dispB
        
    def get_Z(self, msg):
        self.query('A4')
        time.sleep(0.02)
        rawmsg = self.query(msg)
        for ii, char in enumerate(rawmsg):
            if char == '+' or char == '-':
                start1 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispA = float(rawmsg[start1:len(rawmsg)-count])
                go = False
            except ValueError:
                count += 1
        rawmsg2 = rawmsg[len(rawmsg)-count:]
        for ii, char in enumerate(rawmsg2):
            if char == '+' or char == '-':
                start2 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispB =  float(rawmsg2[start2:len(rawmsg2)-count])
                go = False
            except ValueError:
                count += 1
        return dispA, dispB
        

    def get_capacitance(self):
        """fetch just capacitance [pF]"""
        return self.get_front_panel()[1]

    def get_freq(self):
        """fetch frequency from front panel in Hz"""
        return self.get_front_panel()[0]

    def get_frequency(self):
        """fetch the value the frequency is set to in Hertz"""
        return self.freq

    def get_front_panel(self):
        """fetch frequency [Hz], capacitance [pF], loss [default is tan(delta)], and voltage [V]"""
        freq_dict = {10e3: 'F11',
                     20e3: 'F12',
                     40e3: 'F13',
                     100e3: 'F14',
                     200e3: 'F15',
                     400e3: 'F16',
                     1e6: 'F17',
                     2e6: 'F18',
                     4e6: 'F19',
                     10e6: 'F20'}
        msg = freq_dict[self.freq]
        caps = np.zeros((self.aves))
        losses = np.zeros((self.aves))
        # throw away first 6 measurements
        for ii in xrange(4):
            throw_away_cap, throw_away_loss = self.getCL(msg)
        for ii in xrange(self.aves):
            caps[ii], losses[ii] = self.getCL(msg)
            #caps[ii], losses[ii] = self.get_RC(msg)
        cap = sum(caps)/(self.aves)
        if cap > 1000000.:
            cap = 0
        loss = sum(losses)/(self.aves)
        msgout = [self.freq, cap, loss, self.measure_volt]
        return msgout
        
    def get_front_panel_Z(self):
        freq_dict = {10e3: 'F11',
                     20e3: 'F12',
                     40e3: 'F13',
                     100e3: 'F14',
                     200e3: 'F15',
                     400e3: 'F16',
                     1e6: 'F17',
                     2e6: 'F18',
                     4e6: 'F19',
                     10e6: 'F20'}
        msg = freq_dict[self.freq]
        Zs = np.zeros((self.aves))
        thetas = np.zeros((self.aves))
        for ii in xrange(4):
            throw_away_Z, throw_away_theta = self.get_Z(msg)
        for ii in xrange(self.aves):
            Zs[ii],  thetas[ii] = self.get_Z(msg)
        Z = sum(Zs)/(self.aves)
        theta = sum(thetas)/(self.aves)
        msgout = [self.freq, Z, theta*np.pi/180., self.measure_volt]
        return msgout
                    
        
        
    def get_front_panel_RC(self):
        freq_dict = {10e3: 'F11',
                     20e3: 'F12',
                     40e3: 'F13',
                     100e3: 'F14',
                     200e3: 'F15',
                     400e3: 'F16',
                     1e6: 'F17',
                     2e6: 'F18',
                     4e6: 'F19',
                     10e6: 'F20'}
        msg = freq_dict[self.freq]
        resses = np.zeros((self.aves))
        caps = np.zeros((self.aves))
        # throw away first 6 measurements
        for ii in xrange(10):
            throw_away_res, throw_away_cap = self.get_RC(msg)
        for ii in xrange(self.aves):
            resses[ii], caps[ii] = self.get_RC(msg)
        res = sum(resses)/(self.aves)
        #if cap > 10.:
        #    cap = 0
        cap = sum(caps)/(self.aves)
        msgout = [self.freq, res, cap, self.measure_volt]
        return msgout

    def get_loss(self, units=False):
        """Fetch just loss [check units], give units=True to also print units"""
        if units:
            return (self.get_front_panel()[2], self.get_units())
        return self.get_front_panel()[2]

    def get_units(self):
        """Fetch units for loss"""
        pass        
        #msgout = self.write('SH UN').strip('\n')
        #return msgout[-2:]

    def get_volt(self):
        """Fetch voltage setting for capacitance measurement in V"""
        return self.get_front_panel()[3]

    def id(self):
        """Get device id"""
        return self.write('*IDN?')


    def set_freq(self, inHertz):
        """Sets the frequency on capacitor
        give inHertz None or False and give 'UP' or 'DO' to adjust frequency by one "notch"
        otherwise, just give a number for inHertz in.. Hertz"""
        if inHertz < 15e3:
            freq = 10e3
        elif inHertz < 35e3:
            freq = 20e3
        elif inHertz < 75e3:
            freq = 40e3
        elif inHertz < 150e3:
            freq = 100e3
        elif inHertz < 300e3:
            freq = 200e3
        elif inHertz < 750e3:
            freq = 400e3
        elif inHertz < 1.5e6:
            freq = 1e6
        elif inHertz < 3e6:
            freq = 2e6
        elif inHertz < 7.5e6:
            freq = 4e6
        else:
            freq = 10e6
        self.freq = freq

        
    def dcbias(self, msgin):
        """if msgin.lower() == 'off':
            msgout = 'BIAS OFF'
            printmsg = 'DC Bias off'
        elif msgin.lower() == 'high' or msgin.lower() == 'hi':
            msgout = 'BIAS IHIGH'
            printmsg = 'DC Bias set to high'
        elif msgin.lower() == 'low' or msgin.lower() == 'lo':
            msgout = 'BIAS ILOW'
            printmsg = 'DC Bias set to low'
        self.write2(msgout)
        print printmsg"""
        pass
    
    def set_ave(self, msg):
        self.aves = int(msg)

    def set_units(self, unit='DS'):
        """Set units for loss, default is dissipation factor tan(delta)
        NS: nanosiemens, KO: series resistances in kOhms, GO: Parallel R in GOhms, JP: G/omega"""
        #self.write2('UN %s' % unit)
        pass

    def set_voltage(self, volt=1):
        """set the voltage of the sine wave the AH uses to make measurements"""
        self.measure_volt = volt
        #self.write2('V %s' % str(volt))

    def sleep(self, time_to_wait, tag1='', tag2=''):
        """A custom sleep command that writes dots to console so you know what's going on"""
        sys.stdout.write(tag1)
        sys.stdout.flush()
        for second in xrange(int(time_to_wait)):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        time.sleep(time_to_wait-int(time_to_wait))
        sys.stdout.write(' %s\n' % tag2)
        sys.stdout.flush()

    def trigger(self):
        """Need to trigger to initiate"""
        self.write2('*TR')
        print 'Triggered'


if __name__ == '__main__':
    import get

    bridge = dev(28, get.serialport())
    print bridge.id()
    print bridge.get_capacitance()
    print bridge.get_front_panel()
