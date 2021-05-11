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


class DataFile:

    cryo_to_ls = {'DESERT-LN': 340, 'DESERT-HE': 340, '40K': 331, '4K': None}

    def __init__(self, path, filename, port, unique_freqs, bridge='AH', cryo='40K', comment='', lj_chs=[]):
        """Create data file, and instances of the bridge and Lakeshore for communication"""
        self.name = os.path.join(path, filename)
        print(unique_freqs)
        list.sort(unique_freqs)
        self.unique_freqs = unique_freqs[::-1]
        if '.csv' not in self.name:
            self.name += '.csv'  # if there's no .csv, append it on the end
        self.write_row2("# This {} data file was created on {}".format(purpose, time.ctime(time.time())))
        self.write_row2('# {}'.format(comment))

        if bridge.upper()[0:2] == 'AH':
            self.bridge = AH2700A(port)
        elif bridge.upper()[0:2] == 'HP':
            self.bridge = HP4275A(port)
        self.ls = LakeShore(port, self.cryo_to_ls[cryo.upper()])

        if len(lj_chs) > 0:
            self.lj = LabJack.LabJack()
            print('imported LabJack')
        else:
            self.lj = None
            print('did not import LabJack')
        labels = []
        self.set_labels()

    def set_labels(self):
        pass


class CalFile(DataFile):

    def set_lables(self):
        for freq in self.unique_freqs:
            f = str(int(freq))
            if len(f) <= 3:
                f += 'Hz'
            elif len(f) <= 6:
                f = f[:-3] + 'kHz'
            elif len(f) <= 9:
                f = f[:-6] + 'MHz'
            disp_A = 'Capacitance'
            unit_A = '[pF]'
            disp_B = 'Loss Tangent'
            unit_B = ''
            labels.extend(['Time {} [s]'.format(f),
                           'Temperature A {} [K]'.format(f),
                           'Temperature B {} [K]'.format(f),
                           ('{} {} {}'.format(disp_A, f, unit_A)).strip(' '),
                           ('{} {} {}'.format(disp_B, f, unit_B)).strip(' '),
                           'Voltage {} [V]'.format(f)])
            if type(self.lj_chs) == list:
                for ii, ch in enumerate(lj_chs):
                    labels.insert(3 + ii * 9, 'LJ AIN{} {} [V]'.format(ch, f))
                    labels.insert(4 + ii * 9, 'Std Dev AIN{} {} [V]'.format(ch, f))
            labels.append('Frequency {} [Hz]'.format(f))
            self.write_row2(labels)

    def sweep_freq_win(self, amp=1, offset=0):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        data_to_write = []
        for ii, freq in enumerate(self.unique_freqs):
            self.bridge.set_freq(freq)
            time.sleep(0.1)
            print('frequency set')
            good = 0
            while not good:
                try:
                    if 'resistance' in self.filename.lower():
                        temp_data = self.bridge.get_front_panel_RC()
                    else:
                        temp_data = self.bridge.get_front_panel()
                    good = 1
                except:  # VisaIOError:
                    pass
                    # print 'ERROR'
                # temp_data = self.bridge.get_front_panel()
            print('read front panel')
            if temp_data[0] == '':
                print('failed to read front panel, trying again...')
                if 'resistance' in self.filename.lower():
                    temp_data = self.bridge.get_front_panel_RC
                else:
                    temp_data = self.bridge.get_front_panel()
            temperature1 = self.ls.get_temp('A')
            temperature2 = self.ls.get_temp('B')
            if len(temp_data) == 4:
                f = temp_data[0]
                c = temp_data[1]
                l = temp_data[2]
                v = temp_data[3]
                data_f = [time.time(), temperature1, temperature2, c, l, v]
                if type(self.lj_chs) == list:
                    if len(self.lj_chs) > 0:
                        lj_val, lj_err = list(np.array(list(chain(*self.lj.get_voltages_ave(self.lj_chs)))) * amp)
                        data_f.insert(3, lj_val + offset)
                        data_f.insert(4, lj_err)
                data_f.append(f)
            else:
                data_f = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                if self.lj:
                    data_f.extend([-1] * 4)
                self.write_row2('# %s' % temp_data[0])
            print(data_f)
            data_to_write.extend(data_f)
        self.write_row2(data_to_write)



    def write_row(self, row_to_write):
        with open(self.name, 'wb') as csvfile:
            self.data_writer = csv.writer(csvfile, delimiter=',', quotechar='|')
            self.data_writer.writerow(row_to_write)

    def write_row2(self, row_to_write):
        with open(self.name, 'a') as f:
            f.write(str(row_to_write).strip('[').strip(']').replace("'", "") + '\n')

    '''def dc_bias_measurement(self, freqs, measurements_at_each_volt, dc_bias_values, amp=1, offset=0.):
        """the numbers you give it for dc_bias_values are the voltages you want. set amp to the amplifier's
        amplification, and it will divide by this number, to set the labjack at an appropriate value to be amplified
        to the desired value."""
        print('Starting a set of DC Bias measurements')
        print('Will measure these frequencies (in Hz): %s, %d times' % (freqs, measurements_at_each_volt))
        # print 'Will measure at all these DC bias values (in volts): %s with an amplifier of %0.2f amplification'\
        #      % (dc_bias_values, amp)
        for dc_bias_value in dc_bias_values:
            self.lj.set_dc_voltage2(dc_bias_value, amp=amp)
            for _ in range(measurements_at_each_volt):
                self.sweep_freq_win(amp, offset=offset)
        self.lj.set_dc_voltage2(0, amp=amp)

    def check_hysteresis(self, low, high, freqs, measure_per_freq, wait=0):
        """Check thermal hysteresis"""
        if low > high:
            temp_var = low
            low = float(high)
            high = float(temp_var)
        print('Starting temperature sweep measurements')
        print('Measuring between %dK and %dK' % (low, high))
        # print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        print('Will wait %d seconds once %dK is reached' % (wait, high))
        temperature1 = self.ls.get_temp('A')
        setpoints = [high, low]
        for ii, setpt in enumerate(setpoints):
            self.ls.setpoint(setpt)
            print('Set temperature to %.2fK. Waiting to reach setpoint' % setpt)
            while abs(temperature1 - setpt) > 0.01:
                for freq in freqs:
                    for k in range(measure_per_freq):
                        self.bridge.set_freq(freq)
                        temp_data = self.bridge.get_front_panel()
                        temperature1 = self.ls.get_temp('A')
                        temperature2 = self.ls.get_temp('B')
                        data_to_write = [time.time(), temperature1, temperature2] + temp_data
                        print(data_to_write)
                        self.write_row2(data_to_write)
            if ii == 0:
                print("Reached %dK" % high)
                if wait > 0:
                    print("Now waiting %d seconds" % wait)
                    then = time.time()
                    while abs(time.time() - then) < wait:
                        for freq in freqs:
                            for ii in range(measure_per_freq):
                                self.bridge.set_freq(freq)
                                temp_data = self.bridge.get_front_panel()
                                temperature1 = self.ls.get_temp('A')
                                temperature2 = self.ls.get_temp('B')
                                data_to_write = [time.time(), temperature1, temperature2] + temp_data
                                print(data_to_write)
                                self.write_row2(data_to_write)
                print("done")
                self.speak('Reached %dK' % high)
            elif ii == 1:
                print("Reached %dK" % low)
                self.speak('Reached %dK' % low)

    def check_hysteresis2(self, low, high, freqs, measure_per_freq):
        """Check thermal hysteresis"""
        if low > high:
            temp_var = low
            low = float(high)
            high = float(temp_var)
        print('Starting temperature sweep measurements')
        print('Measuring between %dK and %dK' % (low, high))
        # print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        print('Will wait for you to press enter once setpoints are reached to continue')
        temperature1 = self.ls.get_temp('A')
        setpoints = [high, low]
        for ii, setpt in enumerate(setpoints):
            self.ls.setpoint(setpt)
            print('Set temperature to %.2fK. Waiting to reach setpoint' % setpt)
            while abs(temperature1 - setpt) > 0.01:
                for freq in freqs:
                    for k in range(measure_per_freq):
                        self.bridge.set_freq(freq)
                        try:
                            temp_data = self.bridge.get_front_panel()
                            # if temp_data[1] < 1.:
                            #    """if capacitance reads too low throw out that point"""
                            #    raise IOError('Capacitance reading too low')
                            temperature1 = self.ls.get_temp('A')
                            temperature2 = self.ls.get_temp('B')
                            data_to_write = [time.time(), temperature1, temperature2] + temp_data
                            print(data_to_write)
                            self.write_row2(data_to_write)
                        except IOError:
                            print('Timed out reading from bridge, resetting bridge')
                            self.bridge.clear()
                            self.bridge.reset()
                        # except ValueError:
                        #    t = threading.Thread(target=self.speak('Probes lifted, please fix them'))
                        #    t.start()
                        #    print "Probes lifted, please fix them."
                        #    raw_input("Press Enter to continue...")
                        #    self.bridge.clear()
                        #    self.bridge.reset()
            print("Reached %dK" % setpt)
            self.speak('Reached %dK' % setpt)
            print("Now waiting for you to press Enter to continue")
            self.speak('Press the enter key to continue')
            wait = True
            while wait:
                print("Press Enter to Continue")
                for freq in freqs:
                    for ii in range(measure_per_freq):
                        self.bridge.set_freq(freq)
                        temp_data = self.bridge.get_front_panel()
                        temperature1 = self.ls.get_temp('A')
                        temperature2 = self.ls.get_temp('B')
                        data_to_write = [time.time(), temperature1, temperature2] + temp_data
                        print(data_to_write)
                        self.write_row2(data_to_write)
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = input()
                    wait = False
            print("done")

    def cont_meas(self, freq):
        """Continuously monitor capacitance until manual break (ctrl+C)"""
        print('Starting continuous measurement. Press ctrl+C to end data taking')
        print('Measuring at %d Hz' % freq)
        self.bridge.set_freq(freq)
        while True:
            temp_data = self.bridge.get_front_panel()
            temperature1 = self.ls.get_temp('A')
            temperature2 = self.ls.get_temp('B')
            data_to_write = [time.time(), temperature1, temperature2] + temp_data
            print(data_to_write)
            self.write_row2(data_to_write)

    def cool_down(self, freqs, cryo='Nitrogen'):
        """Continuously measure while cooling"""
        cryo = cryo.lower()
        if cryo[0] == 'n':
            setpt = 70
        elif cryo[0] == 'h':
            setpt = 3
        else:
            raise ValueError("please enter Nitrogen or Helium for cryo")
        print('Starting measurements of ')

    def dcbias(self, msg):
        self.bridge.dcbias(msg)
        self.write_row2('# DC bias set to %s' % msg)

    def bake(self, high, step_size, freqs, measure_per_freq, hold_time=60):
        """Raise temperature to desired temperature and monitor along the way. Will continue to
        monitor until manual break"""
        print('Starting temperature sweep measurements')
        print('Measuring to %dK with steps of %d' % (high, step_size))
        print('Measuring at these frequencies [Hz] %s' % str(freqs))
        low = int(self.ls.get_temp('A'))
        setpoints = np.arange(low, high + step_size, step_size)
        for ii, setpt in enumerate(setpoints):
            if setpt > 400:
                setpt = 400
            hold = hold_time
            self.ls.setpoint(setpt)
            print('Set temperature to %.2fK Waiting to reach setpoint' % setpt)
            while hold > 0:
                temperature1 = self.ls.get_temp('A')
                sys.stdout.write('.')
                sys.stdout.flush()
                if abs(temperature1 - setpt) < 0.01:
                    hold -= 1
            print(' done waiting')
            for freq in freqs:
                self.bridge.set_freq(freq)
                for ii in range(measure_per_freq):
                    temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    data_to_write = [time.time(), temperature1, temperature2] + temp_data
                    print(data_to_write)
                    self.write_row2(data_to_write)
        while True:
            self.sweep_freq(freqs, 3)

    def sweep_freq(self, freqs, measurements_at_each_freq):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        for freq in freqs:
            self.bridge.set_freq(freq)
            for ii in range(measurements_at_each_freq):
                if 1:
                    temp_data = self.bridge.get_front_panel()
                    if temp_data[0] == '':
                        print('failed to read front panel, trying again...')
                        temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        data_to_write = [time.time()] + blah
                        if 'dc' in self.filename:
                            # print self.lj.get_dc_voltage()
                            data_to_write.append(self.lj.get_dc_voltage())
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                        if 'dc' in self.filename:
                            data_to_write.append(-1)
                        self.write_row2('# %s' % temp_data[0])
                    print(data_to_write)
                    self.write_row2(data_to_write)'''

    '''def sweep_freq_win_return(self, amp=1, offset=0):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        data_to_write = []
        Cret = np.zeros(len(self.unique_freqs))
        Lret = np.zeros(len(self.unique_freqs))
        for ii, freq in enumerate(self.unique_freqs):
            self.bridge.set_freq(freq)
            time.sleep(0.1)
            print('frequency set')
            good = 0
            while not good:
                try:
                    temp_data = self.bridge.get_front_panel()
                    good = 1
                except VisaIOError:
                    pass
            print('read front panel')
            if temp_data[0] == '':
                print('failed to read front panel, trying again...')
                temp_data = self.bridge.get_front_panel()
            temperature1 = self.ls.get_temp('A')
            temperature2 = self.ls.get_temp('B')
            if len(temp_data) == 4:
                f = temp_data[0]
                c = temp_data[1]
                Cret[ii] = c
                l = temp_data[2]
                Lret[ii] = l
                v = temp_data[3]
                data_f = [time.time(), temperature1, temperature2, c, l, v]
                if type(self.lj_chs) == list:
                    if len(self.lj_chs) > 0:
                        lj_val, lj_err = list(np.array(list(chain(*self.lj.get_voltages_ave(self.lj_chs)))) * amp)
                        data_f.insert(3, lj_val + offset)
                        data_f.insert(4, lj_err)
                data_f.append(f)
            else:
                data_f = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                if self.lj:
                    data_f.extend([-1] * 4)
                self.write_row2('# %s' % temp_data[0])
            print(data_f)
            data_to_write.extend(data_f)
        self.write_row2(data_to_write)
        return Cret, Lret

    def sweep_freq_win_RC(self, amp=1, offset=0):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        data_to_write = []
        for ii, freq in enumerate(self.unique_freqs):
            self.bridge.set_freq(freq)
            time.sleep(0.1)
            print('frequency set')
            temp_data = self.bridge.get_front_panel_RC()
            print('read front panel')
            if temp_data[0] == '':
                print('failed to read front panel, trying again...')
                temp_data = self.bridge.get_front_panel_RC()
            temperature1 = self.ls.get_temp('A')
            temperature2 = self.ls.get_temp('B')
            if len(temp_data) == 4:
                f = temp_data[0]
                r = temp_data[1]
                c = temp_data[2]
                v = temp_data[3]
                data_f = [time.time(), temperature1, temperature2, r, c, v]
                if type(self.lj_chs) == list:
                    if len(self.lj_chs) > 0:
                        lj_val, lj_err = list(np.array(list(chain(*self.lj.get_voltages_ave(self.lj_chs)))) * amp)
                        data_f.insert(3, lj_val + offset)
                        data_f.insert(4, lj_err)
                data_f.append(f)
            else:
                data_f = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                if self.lj:
                    data_f.extend([-1] * 4)
                self.write_row2('# %s' % temp_data[0])
            print(data_f)
            data_to_write.extend(data_f)
        self.write_row2(data_to_write)

    def sweep_freq_win_Z(self, amp=1, offset=0):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        data_to_write = []
        for ii, freq in enumerate(self.unique_freqs):
            self.bridge.set_freq(freq)
            time.sleep(0.1)
            print('frequency set')
            temp_data = self.bridge.get_front_panel_Z()
            print('read front panel')
            if temp_data[0] == '':
                print('failed to read front panel, trying again...')
                temp_data = self.bridge.get_front_panel_Z()
            temperature1 = self.ls.get_temp('A')
            temperature2 = self.ls.get_temp('B')
            if len(temp_data) == 4:
                f = temp_data[0]
                r = temp_data[1]
                c = temp_data[2]
                v = temp_data[3]
                data_f = [time.time(), temperature1, temperature2, r, c, v]
                if type(self.lj_chs) == list:
                    if len(self.lj_chs) > 0:
                        lj_val, lj_err = list(np.array(list(chain(*self.lj.get_voltages_ave(self.lj_chs)))) * amp)
                        data_f.insert(3, lj_val + offset)
                        data_f.insert(4, lj_err)
                data_f.append(f)
            else:
                data_f = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                if self.lj:
                    data_f.extend([-1] * 4)
                self.write_row2('# %s' % temp_data[0])
            print(data_f)
            data_to_write.extend(data_f)
        self.write_row2(data_to_write)

    def sweep_freq_old2(self, freqs, measurements_at_each_freq):
        # global first
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        # print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        # print 'Measuring %d times at each frequency' % measurements_at_each_freq
        # if first:
        #    self.ls.read(3)
        #    first = 0
        for freq in freqs:
            self.bridge.set_freq(freq)
            for ii in range(measurements_at_each_freq):
                # try:
                if 1:
                    # temp_data = self.bridge.get_front_panel()
                    # print temp_data
                    # time.sleep(2)
                    # temp_data = [100, 1.2, 5, 15]
                    # get_temp = True
                    # while get_temp:
                    #    try:
                    #        temperature1 = self.ls.get_temp('A')
                    #        # print temperature1
                    #        temperature2 = self.ls.get_temp('B')
                    #        # print temperature2
                    #        get_temp = False
                    #    except IOError:
                    #        print "failed to get temperatures"
                    #        reload(LS340)
                    #        self.ls = LS340.dev(12, get.serialport())
                    temp_data = self.bridge.get_front_panel()
                    if temp_data[0] == '':
                        print('failed to read front panel, trying again...')
                        temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    # temperature2 = self.ls.get_temp('B')
                    temperature2 = self.ls.get_temp('B')
                    # print temperature1
                    # print temperature2
                    # print temp_data
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                        # print temp_data
                    # print temp_data
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        # print blah
                        data_to_write = [time.time()] + blah  # , temperature1, temperature2] + temp_data[:-1]
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                        self.write_row2('# %s' % temp_data[0])
                    print(data_to_write)
                    self.write_row2(data_to_write)
                    # except IOError:
                    #    print 'Timed out reading from bridge, resetting bridge'
                    #    self.bridge.clear()
                    #    self.bridge.reset()
                    # except ValueError:
                    #    t = threading.Thread(target=self.speak('Probes lifted, please fix them'))
                    #    t.start()
                    #    print "Probes lifted, please fix them."
                    #    raw_input("Press Enter to continue...")
                    #    self.bridge.clear()
                    #    self.bridge.reset()

    def sweep_freq_old(self, freqs, measurements_at_each_freq):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        print('Measuring at these frequencies [Hz] %s' % str(freqs))
        print('Measuring %d times at each frequency' % measurements_at_each_freq)
        # self.ls.read(3)
        for freq in freqs:
            self.bridge.set_freq(freq)
            for ii in range(measurements_at_each_freq):
                # try:
                if 1:
                    # temp_data = self.bridge.get_front_panel()
                    # print temp_data
                    # time.sleep(2)
                    # temp_data = [100, 1.2, 5, 15]
                    get_temp = True
                    while get_temp:
                        try:
                            temperature1 = self.ls.get_temp('A')
                            # print temperature1
                            temperature2 = self.ls.get_temp('B')
                            # print temperature2
                            get_temp = False
                        except IOError:
                            print("failed to get temperatures")
                            # reload(lakeshore_client)
                            reload(LS340)
                            # self.ls = lakeshore_client.Lakeshore()
                            self.ls = LS340.dev(12, get.serialport())
                    temp_data = self.bridge.get_front_panel()
                    # print temp_data
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                        # print temp_data
                    # print temp_data
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        print(blah)
                        data_to_write = [time.time()] + blah  # , temperature1, temperature2] + temp_data
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1]
                        self.write_row2('# %s' % temp_data[0])
                    print(data_to_write)
                    self.write_row2(data_to_write)
                # except IOError:
                #    print 'Timed out reading from bridge, resetting bridge'
                #    self.bridge.clear()
                #    self.bridge.reset()
                # except ValueError:
                #    t = threading.Thread(target=self.speak('Probes lifted, please fix them'))
                #    t.start()
                #    print "Probes lifted, please fix them."
                #    raw_input("Press Enter to continue...")
                #    self.bridge.clear()
                #    self.bridge.reset()

    def sweep_heat(self, low, high, step_size, freqs, measure_per_freq, hold_time=60):
        """Sweep frequencies and temperature to understand thermal hysteresis"""
        if low > high:
            temp_var = low
            low = float(high)
            high = float(temp_var)
        print('Starting temperature sweep measurements')
        print('Measuring between %dK and %dK with steps of %d' % (low, high, step_size))
        print('Measuring at these frequencies [Hz] %s' % str(freqs))
        temperature1 = self.ls.get_temp('A')
        low_to_high = np.arange(low, high + step_size, step_size)
        high_to_low = low_to_high[::-1]
        if abs(low - temperature1) < abs(high - temperature1) / 3:
            setpoints = np.concatenate((low_to_high, high_to_low))
            holdfactor = 1  # when holdfactor is 2, it slows down the hold time by a factor of 2
        else:
            setpoints = np.concatenate((high_to_low, low_to_high))
            holdfactor = 4
        for ii, setpt in enumerate(setpoints):
            if ii > 1:
                if setpoints[ii] >= setpoints[ii - 1]:
                    holdfactor = 1
                else:
                    holdfactor = 4
            hold = hold_time * holdfactor
            self.ls.setpoint(setpt)
            print('Set temperature to %.2fK Waiting to reach setpoint' % setpt)
            while hold > 0:
                temperature1 = self.ls.get_temp('A')
                sys.stdout.write('.')
                sys.stdout.flush()
                if abs(temperature1 - setpt) < 0.01:
                    hold -= 1
            print(' done waiting')
            for freq in freqs:
                for ii in range(measure_per_freq):
                    self.bridge.set_freq(freq)
                    temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    data_to_write = [time.time(), temperature1, temperature2] + temp_data[:-1]
                    print(data_to_write)
                    self.write_row2(data_to_write)'''


class Instrument:
    def __init__(self, abbr, port):
        self.abbr = abbr
        self.port = port

    def query(self, msg):
        return send('{}::QU::{}'.format(self.abbr, msg), self.port)

    def write(self, msg):
        send('{}::WR::{}'.format(self.abbr, msg), self.port)

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
            msgout = rawmsg
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
        self.frequency = 10e3
        self.aves = 1
        self.measure_volt = 1
        self.dispA = 'C'
        self.dispB = 'D'
        #self.set_dispA(self.dispA)
        #self.set_dispB(self.dispB)


    def clear(self):
        """Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device."""
        self.write('DC1')
        print('Cleared HP bridge')

    def read_CL(self, freq_code):
        self.write('A2')
        time.sleep(0.02)
        self.write('B1')
        time.sleep(0.02)
        rawmsg = self.query(freq_code)
        for ii, char in enumerate(rawmsg):
            if char == '+' or char == '-':
                start1 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispA = float(rawmsg[start1:len(rawmsg) - count])
                go = False
            except ValueError:
                count += 1
        rawmsg2 = rawmsg[len(rawmsg) - count:]
        for ii, char in enumerate(rawmsg2):
            if char == '+' or char == '-':
                start2 = ii
                break
        go = True
        count = 0
        while go:
            try:
                dispB = float(rawmsg2[start2:len(rawmsg2) - count])
                go = False
            except ValueError:
                count += 1
        return dispA * 1e12, dispB

    def read_front_panel(self):
        """fetch frequency [Hz], capacitance [pF], loss [default is tan(delta)], and voltage [V]"""
        freq_msg = self.valid_freqs[self.frequency]
        caps = np.zeros(self.aves)
        losses = np.zeros(self.aves)
        # throw away first 6 measurements
        #for ii in range(4):
        #    _, _ = self.read_CL(freq_msg)
        for ii in range(self.aves):
            caps[ii], losses[ii] = self.query(freq_msg)
        cap = sum(caps) / self.aves
        if cap > 1000000.:
            cap = 0
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
            freq = int(inHertz)
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
    def __init__(self, port, inst_num=340):
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
        return float(self.heater_ranges[self.query('RANGE?')])

    def read_PID(self, loop=1):
        """Returns PID values nnnn.n,nnnn.n,nnnn"""
        msg_back = self.query('PID? {}'.format(loop)).split(',')
        P = float(msg_back[0])
        I = float(msg_back[1])
        D = float(msg_back[2])
        return [P, I, D]

    def read_ramp_speed(self, loop=1):
        """Kelvin per minute"""
        response = self.query('RAMP? {}'.format(loop))
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
        return self.query('SETP? {}'.format(loop))

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
        self.write3('SETP {}, {}' % (loop, float(value)))


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
