import csv
import time
import os
from itertools import chain
import numpy as np
import select
import sys; sys.path.append('../GPIB'); sys.path.append('../Server_scripts')
import AH2700A
import LS340
#import lakeshore_client
import LabJack
import get
import platform
if platform.system() == 'Windows':
    win = True
else:
    win = False

#first = 1


def takeInput():
    """This function will be executed via thread"""
    value = raw_input("Type 'go' to continue")
    return value


class data_file:
    def __init__(self, path, filename, unique_freqs=None, comment='', lj_chs=[], sorter=None):
        """Create data file, and instances of the bridge and lakeshore for communication"""
        self.name = os.path.join(path, filename)
        self.filename = filename.lower()
        list.sort(unique_freqs)
        self.unique_freqs = unique_freqs[::-1]
        if '.csv' not in self.name:
            self.name += '.csv'     # if there's no .csv, append it on the end
        self.write_row2("# This data file was created on %s" % time.ctime(time.time()))
        self.write_row2('# %s' % comment)
        
        if sorter:
            self.bridge = None
            self.ls = None
        else:
            self.bridge = AH2700A.dev(28, get.serialport())
            self.ls = LS340.dev(12, get.serialport())
        self.lj_chs = lj_chs
        
        if len(lj_chs) > 0:
            if 1:            
                #try:
                self.lj = LabJack.LabJack()
                print 'imported labjack'
            #except:
            #    self.lj = None
            #    print 'did not import labjack'
        else:
            self.lj = None
            print 'did not import labjack'
        if self.unique_freqs:
            labels = []
            for freq in self.unique_freqs:
                f = str(int(freq))
                if len(f) < 4:
                    f += 'Hz'
                else:
                    f = f[:-3] + 'kHz'
                labels.extend(['Time %s [s]' % f,
                               'Temperature A %s [K]' % f,
                               'Temperature B %s [K]' % f,
                               'Capacitance %s [pF]' % f,
                               'Loss tangent %s' % f,
                               'Voltage %s [V]' % f])
                if type(self.lj_chs) == list:
                    for ii, ch in enumerate(lj_chs):
                        labels.append('LJ AIN%d %s [V]' % (ch, f))
                        labels.append('Std Dev AIN%d %s [V]' % (ch, f))
                #elif type(self.lj_chs) == str:
                #    if 'dc' in self.lj_chs.lower():
                #        labels.append('DC V %s [V]' % f)
                labels.append('Frequency %s [Hz]' % f)
            self.write_row2(labels)

        else:
            if 'sorted' in filename.lower():
                self.write_row2(['Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'Frequency [Hz]',
                                 'Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'Frequency [Hz]',
                                 'Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'Frequency [Hz]'
                                 ])
            elif 'dc' in filename.lower():
                self.write_row2(['Time [s]', 'Temperature A [K]', 'Temperature B [K]', 'Frequency [Hz]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'DC Voltage [V]'])
            else:
                self.write_row2(['Time [s]', 'Temperature A [K]', 'Temperature B [K]', 'Frequency [Hz]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]'])
        if not win: self.ls.meter.write('++eot_enable')
        #self.bridge.dcbias('hi')

    def speak(self, msg):
        sys.stdout.write('\a')
        sys.stdout.flush()
        os.system('say "%s"' % msg)
        sys.stdout.write('\a\n')

    def dc_bias_measurement(self, freqs, measurements_at_each_freq, dc_bias_values, amp=1):
        """the numbers you give it for dc_bias_values are the voltages you want. set amp to the amplifier's
        amplification, and it will divide by this number, to set the labjack at an appropriate value to be amplified
        to the desired value."""
        print 'Starting a set of DC Bias measurements'
        print 'Will measure these frequencies (in Hz): %s, %d times' % (freqs, measurements_at_each_freq)
        #print 'Will measure at all these DC bias values (in volts): %s with an amplifier of %0.2f amplification'\
        #      % (dc_bias_values, amp)
        for dc_bias_value in dc_bias_values:
            self.lj.set_dc_voltage2(dc_bias_value, amp=amp)
            for freq in freqs:
                self.bridge.set_freq(freq)
                for ii in xrange(measurements_at_each_freq):
                    temp_data = self.bridge.get_front_panel()
                    if temp_data[0] == '':
                        print 'failed to read front panel, trying again...'
                        temp_data = self.bridge.get_front_panel()
                        f = temp_data[1]
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    temperature2 = self.ls.get_temp('B')
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        data_to_write = [time.time()] + blah
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                        self.write_row2('# %s' % temp_data[0])
                    data_to_write.append(self.lj.get_dc_voltage(amp))
                    print data_to_write
                    self.write_row2(data_to_write)
        self.lj.set_dc_voltage(0)


    def check_hysteresis(self, low, high, freqs, measure_per_freq, wait=0):
        """Check thermal hysteresis"""
        if low > high:
            temp_var = low
            low = float(high)
            high = float(temp_var)
        print 'Starting temperature sweep measurements'
        print 'Measuring between %dK and %dK' % (low, high)
        #print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        print 'Will wait %d seconds once %dK is reached' % (wait, high)
        temperature1 = self.ls.get_temp('A')
        setpoints = [high, low]
        for ii, setpt in enumerate(setpoints):
            self.ls.setpoint(setpt)
            print 'Set temperature to %.2fK. Waiting to reach setpoint' % setpt
            while abs(temperature1 - setpt) > 0.01:
                for freq in freqs:
                    for k in xrange(measure_per_freq):
                        self.bridge.set_freq(freq)
                        temp_data = self.bridge.get_front_panel()
                        temperature1 = self.ls.get_temp('A')
                        temperature2 = self.ls.get_temp('B')
                        data_to_write = [time.time(), temperature1, temperature2] + temp_data
                        print data_to_write
                        self.write_row2(data_to_write)
            if ii == 0:
                print "Reached %dK" % high
                if wait > 0:
                    print "Now waiting %d seconds" % wait
                    then = time.time()
                    while abs(time.time() - then) < wait:
                        for freq in freqs:
                            for ii in xrange(measure_per_freq):
                                self.bridge.set_freq(freq)
                                temp_data = self.bridge.get_front_panel()
                                temperature1 = self.ls.get_temp('A')
                                temperature2 = self.ls.get_temp('B')
                                data_to_write = [time.time(), temperature1, temperature2] + temp_data
                                print data_to_write
                                self.write_row2(data_to_write)
                print "done"
                self.speak('Reached %dK' % high)
            elif ii == 1:
                print "Reached %dK" % low
                self.speak('Reached %dK' % low)

    def check_hysteresis2(self, low, high, freqs, measure_per_freq):
        """Check thermal hysteresis"""
        if low > high:
            temp_var = low
            low = float(high)
            high = float(temp_var)
        print 'Starting temperature sweep measurements'
        print 'Measuring between %dK and %dK' % (low, high)
        #print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        print 'Will wait for you to press enter once setpoints are reached to continue'
        temperature1 = self.ls.get_temp('A')
        setpoints = [high, low]
        for ii, setpt in enumerate(setpoints):
            self.ls.setpoint(setpt)
            print 'Set temperature to %.2fK. Waiting to reach setpoint' % setpt
            while abs(temperature1 - setpt) > 0.01:
                for freq in freqs:
                    for k in xrange(measure_per_freq):
                        self.bridge.set_freq(freq)
                        try:
                            temp_data = self.bridge.get_front_panel()
                            #if temp_data[1] < 1.:
                            #    """if capacitance reads too low throw out that point"""
                            #    raise IOError('Capacitance reading too low')
                            temperature1 = self.ls.get_temp('A')
                            temperature2 = self.ls.get_temp('B')
                            data_to_write = [time.time(), temperature1, temperature2] + temp_data
                            print data_to_write
                            self.write_row2(data_to_write)
                        except IOError:
                            print 'Timed out reading from bridge, resetting bridge'
                            self.bridge.clear()
                            self.bridge.reset()
                        #except ValueError:
                        #    t = threading.Thread(target=self.speak('Probes lifted, please fix them'))
                        #    t.start()
                        #    print "Probes lifted, please fix them."
                        #    raw_input("Press Enter to continue...")
                        #    self.bridge.clear()
                        #    self.bridge.reset()
            print "Reached %dK" % setpt
            self.speak('Reached %dK' % setpt)
            print "Now waiting for you to press Enter to continue"
            self.speak('Press the enter key to continue')
            wait = True
            while wait:
                print "Press Enter to Continue"
                for freq in freqs:
                    for ii in xrange(measure_per_freq):
                        self.bridge.set_freq(freq)
                        temp_data = self.bridge.get_front_panel()
                        temperature1 = self.ls.get_temp('A')
                        temperature2 = self.ls.get_temp('B')
                        data_to_write = [time.time(), temperature1, temperature2] + temp_data
                        print data_to_write
                        self.write_row2(data_to_write)
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = raw_input()
                    wait = False
            print "done"

    def cont_meas(self, freq):
        """Continuously monitor capacitance until manual break (ctrl+C)"""
        print 'Starting continuous measurement. Press ctrl+C to end data taking'
        print 'Measuring at %d Hz' % freq
        self.bridge.set_freq(freq)
        while True:
            temp_data = self.bridge.get_front_panel()
            temperature1 = self.ls.get_temp('A')
            temperature2 = self.ls.get_temp('B')
            data_to_write = [time.time(), temperature1, temperature2] + temp_data
            print data_to_write
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
        print 'Starting measurements of '

    def dcbias(self, msg):
        self.bridge.dcbias(msg)
        self.write_row2('# DC bias set to %s' % msg)

    def bake(self, high, step_size, freqs, measure_per_freq, hold_time=60):
        """Raise temperature to desired temperature and monitor along the way. Will continue to
        monitor until manual break"""
        print 'Starting temperature sweep measurements'
        print 'Measuring to %dK with steps of %d' % (high, step_size)
        print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        low = int(self.ls.get_temp('A'))
        setpoints = np.arange(low, high + step_size, step_size)
        for ii, setpt in enumerate(setpoints):
            if setpt > 400:
                setpt = 400
            hold = hold_time
            self.ls.setpoint(setpt)
            print 'Set temperature to %.2fK Waiting to reach setpoint' % setpt
            while hold > 0:
                temperature1 = self.ls.get_temp('A')
                sys.stdout.write('.')
                sys.stdout.flush()
                if abs(temperature1 - setpt) < 0.01:
                    hold -= 1
            print ' done waiting'
            for freq in freqs:
                self.bridge.set_freq(freq)
                for ii in xrange(measure_per_freq):
                    temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    data_to_write = [time.time(), temperature1, temperature2] + temp_data
                    print data_to_write
                    self.write_row2(data_to_write)
        while True:
            self.sweep_freq(freqs, 3)

    def sweep_freq(self, freqs, measurements_at_each_freq):
        """Sweep a set of frequencies"""
        print 'Starting frequency sweep measurements'
        for freq in freqs:
            self.bridge.set_freq(freq)
            for ii in xrange(measurements_at_each_freq):
                if 1:
                    temp_data = self.bridge.get_front_panel()
                    if temp_data[0] == '':
                        print 'failed to read front panel, trying again...'
                        temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        data_to_write = [time.time()] + blah
                        if 'dc' in self.filename:
                            data_to_write.append(self.lj.get_dc_voltage())
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                        if 'dc' in self.filename:
                            data_to_write.append(-1)
                        self.write_row2('# %s' % temp_data[0])
                    print data_to_write
                    self.write_row2(data_to_write)
                    
    def sweep_freq_win(self):
        """Sweep a set of frequencies"""
        print 'Starting frequency sweep measurements'
        data_to_write = []
        for freq in self.unique_freqs:
            self.bridge.set_freq(freq)
            temp_data = self.bridge.get_front_panel()
            if temp_data[0] == '':
                print 'failed to read front panel, trying again...'
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
                        lj_data = list(chain(*self.lj.get_voltages_ave(self.lj_chs)))
                        data_f.extend(lj_data)
                data_f.append(f)
            else:
                data_f = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                if self.lj:
                    data_f.extend([-1]*4)
                self.write_row2('# %s' % temp_data[0])
            print data_f
            data_to_write.extend(data_f)
        self.write_row2(data_to_write)
                    
    def sweep_freq_old2(self, freqs, measurements_at_each_freq):
        #global first
        """Sweep a set of frequencies"""
        print 'Starting frequency sweep measurements'
        #print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        #print 'Measuring %d times at each frequency' % measurements_at_each_freq
        #if first:
        #    self.ls.read(3)
        #    first = 0
        for freq in freqs:
            self.bridge.set_freq(freq)
            for ii in xrange(measurements_at_each_freq):
                # try:
                if 1:
                    # temp_data = self.bridge.get_front_panel()
                    # print temp_data
                    # time.sleep(2)
                    # temp_data = [100, 1.2, 5, 15]
                    #get_temp = True
                    #while get_temp:
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
                        print 'failed to read front panel, trying again...'
                        temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    #temperature2 = self.ls.get_temp('B')
                    temperature2 = self.ls.get_temp('B')
                    #print temperature1
                    #print temperature2
                    #print temp_data
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                        # print temp_data
                    #print temp_data
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        #print blah
                        data_to_write = [time.time()] + blah  # , temperature1, temperature2] + temp_data[:-1]
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1, -1]
                        self.write_row2('# %s' % temp_data[0])
                    print data_to_write
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
        print 'Starting frequency sweep measurements'
        print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        print 'Measuring %d times at each frequency' % measurements_at_each_freq
        #self.ls.read(3)
        for freq in freqs:
            self.bridge.set_freq(freq)
            for ii in xrange(measurements_at_each_freq):
                #try:
                if 1:
                    #temp_data = self.bridge.get_front_panel()
                    #print temp_data
                    #time.sleep(2)
                    #temp_data = [100, 1.2, 5, 15]
                    get_temp = True
                    while get_temp:
                        try:
                            temperature1 = self.ls.get_temp('A')
                            #print temperature1
                            temperature2 = self.ls.get_temp('B')
                            #print temperature2
                            get_temp = False
                        except IOError:
                            print "failed to get temperatures"
                            #reload(lakeshore_client)
                            reload(LS340)
                            #self.ls = lakeshore_client.Lakeshore()
                            self.ls = LS340.dev(12, get.serialport())
                    temp_data = self.bridge.get_front_panel()
                    #print temp_data
                    if len(temp_data) > 4:
                        temp_data = temp_data[1:]
                        #print temp_data
                    #print temp_data
                    if len(temp_data) > 1:
                        blah = [temperature1, temperature2] + temp_data
                        print blah
                        data_to_write = [time.time()] + blah #, temperature1, temperature2] + temp_data
                    else:
                        data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1]
                        self.write_row2('# %s' % temp_data[0])
                    print data_to_write
                    self.write_row2(data_to_write)
                #except IOError:
                #    print 'Timed out reading from bridge, resetting bridge'
                #    self.bridge.clear()
                #    self.bridge.reset()
                #except ValueError:
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
        print 'Starting temperature sweep measurements'
        print 'Measuring between %dK and %dK with steps of %d' % (low, high, step_size)
        print 'Measuring at these frequencies [Hz] %s' % str(freqs)
        temperature1 = self.ls.get_temp('A')
        low_to_high = np.arange(low, high + step_size, step_size)
        high_to_low = low_to_high[::-1]
        if abs(low - temperature1) < abs(high - temperature1)/3:
            setpoints = np.concatenate((low_to_high, high_to_low))
            holdfactor = 1      # when holdfactor is 2, it slows down the hold time by a factor of 2
        else:
            setpoints = np.concatenate((high_to_low, low_to_high))
            holdfactor = 4
        for ii, setpt in enumerate(setpoints):
            if ii > 1:
                if setpoints[ii] >= setpoints[ii-1]:
                    holdfactor = 1
                else:
                    holdfactor = 4
            hold = hold_time * holdfactor
            self.ls.setpoint(setpt)
            print 'Set temperature to %.2fK Waiting to reach setpoint' % setpt
            while hold > 0:
                temperature1 = self.ls.get_temp('A')
                sys.stdout.write('.')
                sys.stdout.flush()
                if abs(temperature1 - setpt) < 0.01:
                    hold -= 1
            print ' done waiting'
            for freq in freqs:
                for ii in xrange(measure_per_freq):
                    self.bridge.set_freq(freq)
                    temp_data = self.bridge.get_front_panel()
                    temperature1 = self.ls.get_temp('A')
                    temperature2 = self.ls.get_temp('B')
                    data_to_write = [time.time(), temperature1, temperature2] + temp_data[:-1]
                    print data_to_write
                    self.write_row2(data_to_write)

    def write_row(self, row_to_write):
        with open(self.name, 'wb') as csvfile:
            self.data_writer = csv.writer(csvfile, delimiter=',', quotechar='|')
            self.data_writer.writerow(row_to_write)

    def write_row2(self, row_to_write):
        with open(self.name, 'a') as f:
            f.write(str(row_to_write).strip('[').strip(']').replace("'", "") + '\n')

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
    #data.sweep_freq(freqs_to_sweep, 1)
    #data.cont_meas(1000)
    #data.bake(400, step_size=20, freqs=freqs_to_sweep, measure_per_freq=3, hold_time=5)
