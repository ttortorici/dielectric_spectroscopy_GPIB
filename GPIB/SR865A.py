import time
import platform
if platform.system() == 'Windows':
    win = True
    from GPIB_NI import GPIB
else:
    win = False
    from GPIB import GPIB_unix
import sys
sys.path.append('../other')

"""Driver for using Andeen Hagerling 2700A Capactiance Bridge"""
# Refer to Section 6 of AH 2700 Firmware 02 Manual.pdf in Manuals and pg 285 on

class dev(GPIB):
    def __init__(self, addr, serialport=''):
        """Connect to Cap Bridge and initialize communications"""
        super(self.__class__, self).__init__(addr, serialport)
        self.devicename = 'SR844'
        self.dev.timeout = 25000
        #self.addr = addr
        #self.port = serialport
        self.set_units('DS')
        # for some reason this doesn't register the first time, but waiting and trying again seems to work
        # this is weird and could be investigated by an anal programmer or GPIB wiz
        #time.sleep(0.01)
        #self.set_units('DS')
        # set to continuous mode, so you can see the measurements on instrument screen
        self.meas_cont(True)
        time.sleep(0.01)
        self.format('ENG', 'ON', 'OF', 'FIX')
        #self.trigger()
        self.ave_time = 0 #fix later
        #self.set_ave(3)
        self.set_ave(self.ave_time)
        self.freq = 10000
        self.set_freq(self.freq)
        #elf.freq = self.get_frequency()

    def clear(self):
        """Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device."""
        self.write2('^U')
        print 'Cleared'

    def dcbias(self, msgin):
        if msgin.lower() == 'off':
            msgout = 'BIAS OFF'
            printmsg = 'DC Bias off'
        elif msgin.lower() == 'high' or msgin.lower() == 'hi':
            msgout = 'BIAS IHIGH'
            printmsg = 'DC Bias set to high'
        elif msgin.lower() == 'low' or msgin.lower() == 'lo':
            msgout = 'BIAS ILOW'
            printmsg = 'DC Bias set to low'
        self.write2(msgout)
        print(printmsg)

    def format(self, notation='ENG', labeling='ON', ieee='OF', fwidth='FIX'):
        """Controls the format and numeric notation of results which are sent to serial or
        GPIB ports. Front panel results are not affected"""
        # capitalize entries
        notation = notation.upper()
        labeling = labeling.upper()
        ieee     = ieee.upper()
        fwidth   = fwidth.upper()
        # notation FLOAT for floating, SCI for scientific, ENG, for engineering
        self.write3('FO NOTAT %s' % notation)
        time.sleep(0.01)
        # enables lables to be sent when set to ON
        self.write3('FO LA %s' % labeling)
        time.sleep(0.01)
        # enables IEEE-488.2 compatible punctuation when set to ON
        self.write3('FO IEE %s' % ieee)
        time.sleep(0.01)
        # fixes field widths when set to FIXED. Permitted values are FIXed and VARiable
        self.write3('FO FW %s' % fwidth)
        print('Formatted')

    def get_capacitance(self):
        """fetch just capacitance [pF]"""
        return self.get_front_panel()[1]

    def get_freq(self):
        """fetch frequency from front panel in Hz"""
        return self.get_front_panel()[0]

    def get_frequency(self):
        """fetch the value the frequency is set to in Hertz"""
        msgout = self.write('SH FR').split()
        # sometimes returns ['FREQUENCY', '1.00000E+03', 'HZ'] and sometimes
        # ['FREQUENCY', '100.00', 'E+00', 'HZ']. cannot convert E+00 to float, but can
        # convert 1E+00 to float
        try:
            order = float('1' + msgout[2])
            freq = float(msgout[2]) * order
        except ValueError:
            freq = float(msgout[1])
        return freq

    def get_front_panel(self):
        """fetch frequency [Hz], capacitance [pF], loss [default is tan(delta)], and voltage [V]"""
        if win:
            rawmsg = self.query('Q')
        else:
            self.open()
            self.ser.write('Q\n')
            #self.read()
            #self.ser.write('Q\n')
            if self.ave_time == 3:
                if self.freq < 100:
                    wait = 25
                elif self.freq < 500:
                    wait = 14.5
                elif self.freq < 1500:
                    wait = 1
                else:
                    wait = 1
            elif self.ave_time == 0:
                if self.freq < 300:
                    wait = 13
                elif self.freq < 500:
                    wait = 8
                elif self.freq < 1500:
                    #wait = 1.5
                    wait = 5
                else:
                    wait = 0.5
            if self.ave_time == 7:
                if self.freq < 500:
                    wait = 14
                elif self.freq < 1500:
                    wait = 3
                else:
                    wait = 1
            if wait >= 1:
                self.sleep(wait, 'Waiting to read from front panel', 'done')
            else:
                time.sleep(wait)
            rawmsg = self.read().strip('\n')  # .split()
            self.close()
        # print msgout
        rawmsg = rawmsg.split('=')
        if len(rawmsg) == 1:
            msgout = rawmsg
        else:
            msgout = []
            for ii, element in enumerate(rawmsg):
                if len(element) > 3:
                    go = True
                    remove = 0
                    while go:
                        try:
                            #print element[:(len(element)-remove)].replace(' ', '')
                            msgout.append(float(element[:(len(element)-remove)].replace(' ', '')))
                            go = False
                        except ValueError:
                            remove += 1
        #print msgout
        #self.meas_cont()
        #return [freq, cap, loss, volt]
        return msgout

    def get_loss(self, units=False):
        """Fetch just loss [check units], give units=True to also print units"""
        if units:
            return (self.get_front_panel()[2], self.get_units())
        return self.get_front_panel()[2]

    def get_units(self):
        """Fetch units for loss"""
        msgout = self.write('SH UN').strip('\n')
        return msgout[-2:]

    def get_volt(self):
        """Fetch voltage setting for capacitance measurement in V"""
        return self.get_front_panel()[3]

    def id(self):
        """Get device id"""
        return self.write('*IDN?')

    def local(self):
        """Activate Front Panel"""
        self.write3('LOC')

    def lockout(self, on=True):
        """When on, locks out front panel entirely; resulting in pressing local on the panel not working"""
        # if given a string, make it a boolean. Will accept 'on' (not case sensitive) as True
        if type(on) == 'str':  # is the parameter given a string?
            on = on.upper()
            if on == 'ON':
                on = True
            else:
                on = False
        if on == True:
            self.write3('NL ON')
        else:
            self.write3('NL OF')

    def meas_cont(self, on=True):
        """Initiates measurements which are taken continuously, one after another"""
        # if given a string, make it a boolean. Will accept 'on' (not case sensitive) as True
        if type(on) == 'str': # is the parameter given a string?
            on = on.upper()
            if on == 'ON':
                on = True
            else:
                on = False
        if on == True:
            self.write3('CO ON')
        else:
            self.write3('CO OF')

    def remote(self):
        """Turn of front panel operation"""
        self.write3('NREM')

    def reset(self):
        """Causes the bridge to reset"""
        self.write3('RST')
        time.sleep(0.1)
        self.__init__(self.addr, self.serialport)

    def set_ave(self, aver_exp):
        """Sets apporximate time used to make a measurement. Set a number between 0 and 15.
        See table A-1 in the Firmware manual on A-10 (pg 246 of the pdf)"""
        try:
            aver_exp = int(aver_exp)
            msg = str(aver_exp)
        except ValueError:
            aver_exp = aver_exp.upper()
            if aver_exp[0] == 'U':
                msg = 'UP'
            elif aver_exp[0] == 'D':
                msg = 'DO'
            else:
                raise ValueError('Please enter a number, or "up" or "down"')
        self.write3('AV %s' % msg)


    def set_freq(self, inHertz):
        """Sets the frequency on capacitor
        give inHertz None or False and give 'UP' or 'DO' to adjust frequency by one "notch"
        otherwise, just give a number for inHertz in.. Hertz"""
        try:
            freq = int(inHertz)
            msg = str(inHertz)
        except ValueError:
            if inHertz[0].lower() == 'u':
                msg = 'UP'
            elif inHertz[0].lower() == 'd':
                msg = 'DO'
            else:
                raise ValueError('Please enter a number, or "up" or "down"')
        self.write3('FR %s' % msg)
        #if inHertz < 80:
        #    wait = 21
        #elif inHertz < 150:
        #    wait = 11
        #elif inHertz < 250:
        #    wait = 6.5
        #elif inHertz < 350:
        #    wait = 3.5
        #elif inHertz < 550:
        #    wait = 3
        #else:
        #    wait = 1
        """if self.ave_time == 0:
            if inHertz < 80:
                wait = 21
            elif inHertz < 150:
                wait = 11
            elif inHertz < 250:
                wait = 8
            elif inHertz < 350:
                wait = 7
            elif inHertz < 550:
                wait = 5
            elif inHertz < 1500:
                wait = 1
            else:
                wait = 1
        else:
            wait = 1
        self.sleep(wait, 'Setting frequency to %d' % inHertz, 'frequency set')"""
        self.freq = inHertz
        #print self.get_frequency()

    def set_units(self, unit='DS'):
        """Set units for loss, default is dissipation factor tan(delta)
        NS: nanosiemens, KO: series resistances in kOhms, GO: Parallel R in GOhms, JP: G/omega"""
        self.write2('UN %s' % unit)

    def set_voltage(self, volt=15):
        """set the voltage of the sine wave the AH uses to make measurements"""
        self.write2('V %s' % str(volt))

    def sleep(self, time_to_wait, tag1='', tag2=''):
        """A custom sleep command that writes dots to console so you know what's going on"""
        sys.stdout.write(tag1)
        sys.stdout.flush()
        for second in range(int(time_to_wait)):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        time.sleep(time_to_wait-int(time_to_wait))
        sys.stdout.write(' %s\n' % tag2)
        sys.stdout.flush()

    def trigger(self):
        """Need to trigger to initiate"""
        self.write2('*TR')
        print('Triggered')


if __name__ == '__main__':
    import get

    bridge = dev(28, get.serialport())
    print(bridge.id())
    print(bridge.get_capacitance())
    print(bridge.get_front_panel())
