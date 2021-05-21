import csv
import time
import os
from itertools import chain
import numpy as np
import select
import platform
import socket
import os
from builtins import input
import sys
import get

if sys.version_info.major > 2:
    if sys.version_info.minor < 4:
        from imp import reload
    else:
        from importlib import reload
if platform.system() == 'Windows':
    win = True
else:
    win = False


def send(msg, port):
    host = '127.0.0.1'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    # message sent to server
    s.send(msg.encode('ascii'))

    # message received from server
    msg_out = s.recv(1024)

    s.close()
    return msg_out.decode('ascii')


class Instrument:
    def __init__(self, abbr, port):
        self.abbr = abbr
        self.port = port

    def query(self, msg):
        return send('{}::QU::{}'.format(self.abbr, msg), self.port)

    def write(self, msg):
        send('{}::WR::{}'.format(self.abbr, msg), self.port)

    def read(self):
        return send('{}::RE::'.format(self.abbr), self.port)

    def read_id(self):
        """Get device id"""
        return self.query('*IDN?')

    def reset(self):
        """Causes the instrument to reset"""
        self.write('*RST')


class AH2700A(Instrument):
    valid_freqs = [50, 60, 70, 80, 100, 120, 140, 160, 200, 240, 300, 400, 500, 600, 700, 800, 1000, 1200, 1400,
                   1600, 2000, 2400, 3000, 4000, 5000, 6000, 7000, 8000, 10000, 12000, 14000, 16000, 20000]

    def __init__(self, port):
        super(self.__class__, self).__init__('AH', port)
        self.frequency = self.read_frequency()
        self.ave = self.read_ave()

    def clear(self):
        """Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device."""
        self.write('^U')
        print('AH2700A cleared')

    def dcbias(self, msgin):
        """Turn DC bias port on or off. Can be set to high current or low current"""
        if msgin.lower() == 'off' or msgin.lower() == 'of':
            msgout = 'BIAS OFF'
            printmsg = 'DC Bias off'
        elif msgin.lower() == 'high' or msgin.lower() == 'hi':
            msgout = 'BIAS IHIGH'
            printmsg = 'DC Bias set to high'
        elif msgin.lower() == 'low' or msgin.lower() == 'lo':
            msgout = 'BIAS ILOW'
            printmsg = 'DC Bias set to low'
        else:
            msgout = ''
            printmsg = 'Invalid DC bias setting'
        self.write(msgout)
        print(printmsg)

    def format(self, notation='ENG', labeling='ON', ieee='OF', fwidth='FIX'):
        """Controls the format and numeric notation of results which are sent to serial or
        GPIB ports. Front panel results are not affected"""
        # capitalize entries
        notation = notation.upper()
        labeling = labeling.upper()
        ieee = ieee.upper()
        fwidth = fwidth.upper()
        # notation FLOAT for floating, SCI for scientific, ENG, for engineering
        self.write('FO NOTAT {}'.format(notation))
        time.sleep(0.01)
        # enables lables to be sent when set to ON
        self.write('FO LA {}'.format(labeling))
        time.sleep(0.01)
        # enables IEEE-488.2 compatible punctuation when set to ON
        self.write('FO IEE {}'.format(ieee))
        time.sleep(0.01)
        # fixes field widths when set to FIXED. Permitted values are FIXed and VARiable
        self.write('FO FW {}'.format(fwidth))
        print('AH2700A formatted')

    def local(self):
        """Activate Front Panel"""
        self.write('LOC')

    def lockout(self, on=True):
        """When on, locks out front panel entirely; resulting in pressing local on the panel not working"""
        # if given a string, make it a boolean. Will accept 'on' (not case sensitive) as True
        if type(on) == 'str':  # is the parameter given a string?
            on = on.upper()
            if on == 'ON':
                on = True
            else:
                on = False
        if on:
            self.write('NL ON')
        else:
            self.write('NL OF')

    def meas_cont(self, on=True):
        """Initiates measurements which are taken continuously, one after another"""
        # if given a string, make it a boolean. Will accept 'on' (not case sensitive) as True
        if type(on) == 'str':  # is the parameter given a string?
            on = on.upper()
            if on == 'ON':
                on = True
            else:
                on = False
        if on:
            self.write('CO ON')
        else:
            self.write('CO OF')

    def read_ave(self):
        """fetch averaging setting"""
        msgout = self.query('SH AV').split('=')
        return int(msgout[1])

    def read_front_panel(self):
        """fetch frequency [Hz], capacitance [pF], loss [default is tan(delta)], and voltage [V]"""
        rawmsg = self.query('Q').split('=')
        if len(rawmsg) == 1:
            msgout = [-1, -1, -1, -1]
        else:
            msgout = []
            for ii, element in enumerate(rawmsg):
                if len(element) > 3:
                    go = True
                    remove = 0
                    while go:
                        try:
                            msgout.append(float(element[:(len(element) - remove)].replace(' ', '')))
                            go = False
                        except ValueError:
                            remove += 1
        # output [freq, cap, loss, volt]
        return msgout

    def read_frequency(self):
        """fetch the value the frequency is set to in Hertz"""
        msgout = self.query('SH FR').split()
        # sometimes returns ['FREQUENCY', '1.00000E+03', 'HZ'] and sometimes
        # ['FREQUENCY', '100.00', 'E+00', 'HZ']. cannot convert E+00 to float, but can
        # convert 1E+00 to float
        try:
            order = float('1' + msgout[2])
            freq = float(msgout[1]) * order
        except ValueError:
            freq = float(msgout[1])
        return freq

    def read_loss_units(self):
        """Fetch units for loss"""
        msgout = self.query('SH UN').strip('\n')
        return msgout[-2:]

    def remote(self):
        """Turn off front panel operation"""
        self.write('NREM')

    def set_ave(self, aver_exp):
        """Sets apporximate time used to make a measurement. Set a number between 0 and 15.
        See table A-1 in the Firmware manual on A-10 (pg 246 of the pdf)"""
        try:
            aver_exp = abs(int(aver_exp))
            if aver_exp > 15:
                aver_exp = 15
            msg = str(aver_exp)
            self.ave = aver_exp
        except ValueError:
            aver_exp = aver_exp.upper()
            if aver_exp[0] == 'U':
                msg = 'UP'
                if self.ave < 15:
                    self.ave += 1
            elif aver_exp[0] == 'D':
                msg = 'DO'
                if self.ave > 0:
                    self.ave -= 1
            else:
                raise ValueError('Please enter a number, or "up" or "down"')
        self.write('AV {}'.format(msg))

    def set_freq(self, inHertz):
        """Sets the frequency on capacitor
        give inHertz None or False and give 'UP' or 'DO' to adjust frequency by one "notch"
        otherwise, just give a number for inHertz in.. Hertz"""
        try:
            freq = int(inHertz)
            """find differences between given inHertz and valid frequencies"""
            difs = [abs(valF - freq) for valF in self.valid_freqs]
            """find smallest difference to find 'nearest' valid frequency"""
            new_freq = self.valid_freqs[difs.index(min(difs))]
            msg = str(new_freq)
            self.frequency = new_freq
        except ValueError:
            if inHertz[0].lower() == 'u':
                msg = 'UP'
                if self.frequency < 20000:
                    self.frequency = self.valid_freqs[self.valid_freqs.index(self.frequency) + 1]
            elif inHertz[0].lower() == 'd':
                msg = 'DO'
                if self.frequency > 50:
                    self.frequency = self.valid_freqs[self.valid_freqs.index(self.frequency) - 1]
            else:
                raise ValueError('Please enter a number, or "up" or "down"')
        self.write('FR {}'.format(msg))
        time.sleep(2)

    def set_units(self, unit='DS'):
        """Set units for loss, default is dissipation factor tan(delta)
        NS: nanosiemens, KO: series resistances in kOhms, GO: Parallel R in GOhms, JP: G/omega"""
        self.write('UN {}'.format(unit))

    def set_voltage(self, volt=15):
        """set the voltage of the sine wave the AH uses to make measurements"""
        self.write('V {}'.format(int(volt)))

    def sleep(self, time_to_wait, tag1='', tag2=''):
        """A custom sleep command that writes dots to console so you know what's going on"""
        sys.stdout.write(tag1)
        sys.stdout.flush()
        for second in range(int(time_to_wait)):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        time.sleep(time_to_wait - int(time_to_wait))
        sys.stdout.write(' {}\n'.format(tag2))
        sys.stdout.flush()

    def trigger(self):
        """Need to trigger to initiate"""
        self.write('*TR')
        print('Triggered')


class HP4275A(Instrument):
    valid_freqs = {10e3: 'F11', 20e3: 'F12', 40e3: 'F13', 100e3: 'F14', 200e3: 'F15',
                   400e3: 'F16', 1e6: 'F17', 2e6: 'F18', 4e6: 'F19', 10e6: 'F20'}
    to_meas_A = {'L': 'A1', 'C': 'A2', 'R': 'A3', 'Z': 'A4'}
    to_meas_B = {'D': 'B1', 'Q': 'B2', 'ESRG': 'B3', 'XB': 'B4', 'LC': 'B5'}

    def __init__(self, port):
        super(self.__class__, self).__init__('HP', port)
        self.frequency = 0
        self.set_freq(10e6)
        self.aves = 1
        self.measure_volt = 1
        self.dispA = 'C'
        self.dispB = 'D'

    def clear(self):
        """Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device."""
        self.write('DC1')
        print('Cleared HP bridge')

    def read_front_panel(self):
        """fetch frequency [Hz], capacitance [pF], loss [default is tan(delta)], and voltage [V]"""
        caps = np.zeros(self.aves)
        losses = np.zeros(self.aves)
        msg = self.read()
        while not msg.strip(' ')[2:4] == 'NC':
            print('waiting for measurement')
            time.sleep(1)
            msg = self.read()
        for ii in range(self.aves):
            msgBack = self.read().split(',')
            caps[ii] = float(msgBack[0][msgBack[0].index('C')+1:])
            losses[ii] = float(msgBack[1][msgBack[1].index('D')+1:])
        cap = sum(caps) / self.aves * 1e12          # put it in pF
        loss = sum(losses) / self.aves
        msgout = [self.frequency, cap, loss, self.measure_volt]
        return msgout

    def set_ave(self, msg):
        self.aves = int(msg)

    def set_dispA(self, to_meas='C'):
        if to_meas.upper() in self.to_meas_A.keys():
            self.write(self.to_meas_A[to_meas])
            self.dispA = to_meas
        else:
            print('invalid display A message (L, C, R, Z)')

    def set_dispB(self, to_meas='D'):
        if to_meas.upper() in self.to_meas_B.keys():
            self.write(self.to_meas_B[to_meas])
            self.dispB = to_meas
        else:
            print('invalid display B message (D, Q, ESRG, XB, LC)')

    def set_freq(self, inHertz):
        """Sets the frequency on capacitor
        give inHertz None or False and give 'UP' or 'DO' to adjust frequency by one "notch"
        otherwise, just give a number for inHertz in.. Hertz"""
        valid_freqs = list(self.valid_freqs.keys())
        try:
            freq = float(inHertz)
            """find differences between given inHertz and valid frequencies"""
            difs = [abs(valF - freq) for valF in valid_freqs]
            """find smallest difference to find 'nearest' valid frequency"""
            self.frequency = valid_freqs[difs.index(min(difs))]
        except ValueError:
            if inHertz[0].lower() == 'u':
                msg = 'UP'
                if self.frequency < 10e6:
                    self.frequency = valid_freqs[valid_freqs.index(self.frequency) + 1]
            elif inHertz[0].lower() == 'd':
                msg = 'DO'
                if self.frequency > 10e3:
                    self.frequency = valid_freqs[valid_freqs.index(self.frequency) - 1]
            else:
                raise ValueError('Please enter a number, or "up" or "down"')
        self.write(self.valid_freqs[self.frequency])
        if self.frequency < 25e3:
            print('wait 60 s')
            time.sleep(60)
        else:
            time.sleep(2)

    def set_voltage(self, volt=1):
        """set the voltage of the sine wave the AH uses to make measurements"""
        self.measure_volt = volt

    def sleep(self, time_to_wait, tag1='', tag2=''):
        """A custom sleep command that writes dots to console so you know what's going on"""
        sys.stdout.write(tag1)
        sys.stdout.flush()
        for second in range(int(time_to_wait)):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        time.sleep(time_to_wait - int(time_to_wait))
        sys.stdout.write(' {}\n'.format(tag2))
        sys.stdout.flush()

    def trigger(self):
        """Need to trigger to initiate"""
        self.write('*TR')
        print('HP bridge Triggered')


class LakeShore(Instrument):
    def __init__(self, port, inst_num=331):
        super(self.__class__, self).__init__('LS', port)
        """correspond heater power (in Watts) with heater range setting"""
        if inst_num == 331:
            self.heater_ranges = [0., 0.5, 5., 50.]
        elif inst_num == 340:
            self.heater_ranges = [0., 0.05, 0.5, 5., 50.]
        self.PID = [0, self.read_PID(1), self.read_PID(2)]

    def read_front_panel(self, units='K'):
        units = units.upper()
        if units in ['K', 'C']:
            temperature_A = float(self.query('{}RDG? A'.format(units)))
            temperature_B = float(self.query('{}RDG? B'.format(units)))
        else:
            raise IOError('Must give units "K" or "C"')
        return [temperature_A, temperature_B]

    def read_heater(self):
        """Query Heater Output. Returns an output in percent"""
        return float(self.query('HTR?'))

    def read_heater_range(self):
        """Returns heater range in Watts"""
        return float(self.heater_ranges[int(self.query('RANGE?'))])

    def read_PID(self, loop=1):
        """Returns PID values nnnn.n,nnnn.n,nnnn"""
        msg_back = self.query('PID? {}'.format(loop)).split(',')
        P = float(msg_back[0])
        I = float(msg_back[1])
        D = float(msg_back[2])
        return [P, I, D]

    def read_ramp_speed(self, loop=1):
        """Kelvin per minute"""
        response = self.query('RAMP? {}'.format(loop)).split(',')
        return float(response[1])

    def read_ramp_status(self, loop=1):
        """Kelvin per minute"""
        return bool(self.query('RAMPST? {}'.format(loop)))

    def read_temp(self, ch='A', units='K'):
        """Get temperature from specified channel. Pass 'C' for units for Celsius"""
        units = units.upper()[0]
        ch = ch.upper()
        if ch in ['A', 'B'] and units in ['K', 'C']:
            msgout = self.query('{}RDG? {}'.format(units, ch))
        else:
            raise IOError('Must give "A" or "B" for ch input and "K" or "C" for units')
        return float(msgout)

    def read_setpoint(self, loop=1):
        """Returns setpoint value in units specified"""
        return float(self.query('SETP? {}'.format(loop)))

    def set_heater_range(self, power_range):
        """Configure Heater range."""
        power_range = abs(float(power_range))
        if power_range in self.heater_ranges:
            self.write('RANGE {}'.format(self.heater_ranges.index(power_range)))
        else:
            raise IOError('Must give a valid heater value in Watts')

    def set_PID(self, P='', I='', D='', loop=1):
        """Configure Control Loop PID Values"""
        if P == '':
            P = self.PID[loop][0]
        else:
            self.PID[loop][0] = float(P)
        if I == '':
            I = self.PID[loop][1]
        else:
            self.PID[loop][1] = float(I)
        if D == '':
            D = self.PID[loop][2]
        else:
            self.PID[loop][2] = float(D)
        self.write('PID {}, {}, {}, {}'.format(loop, P, I, D))

    def set_ramp_speed(self, Kelvin_per_min, loop=1):
        """Set the ramp speed to reach set point in Kelvin per min"""
        self.write('RAMP {}, 1, {}'.format(loop, Kelvin_per_min))

    def set_setpoint(self, value, loop=1):
        """Configure Control loop setpoint.
        loop: specifies which loop to configure.
        value: the value for the setpoint (in whatever units the setpoint is using"""
        self.write('SETP {}, {}'.format(loop, float(value)))


class LabJack(Instrument):
    def __init__(self, port):
        super(self.__class__, self).__init__('LJ', port)

    def read_id(self):
        return 'LabJack U6'

    def reset(self):
        print('One cannot simply reset a LabJack with a command')


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = ''
    if len(sys.argv) > 2:
        comment = sys.argv[2]
    else:
        comment = ''
    data = data_file(os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy'),
                     '%s_%s' % (name, str(time.time()).replace('.', '_')), comment)
    freqs_to_sweep = [500, 1000, 5000, 10000][::-1]
    # data.sweep_freq(freqs_to_sweep, 1)
    # data.cont_meas(1000)
    # data.bake(400, step_size=20, freqs=freqs_to_sweep, measure_per_freq=3, hold_time=5)
