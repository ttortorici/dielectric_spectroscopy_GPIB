import capacitance_measurement_tools as cap
import signal
import os
import time
import datetime
import numpy as np
import sys
import data_sorter as ds
sys.path.append('../GPIB')
import get


max_bias = 100.
bias_step = 10.
offset = 3.
amplification = 100
measurements_per_volt = 3
dcbias_setting = 'LO'
meas_volt = 15
ave_time_setting = 7
freqs_to_sweep = [10000, 1000, 100]


data = []

date = str(datetime.date.today()).split('-')
year = date[0]
month = date[1]
day = date[2]
path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', year, month, day)
filename = 'DC_bias_measurement_%s' % (str(time.time()).replace('.', '_'))
if len(sys.argv) > 1:
    comment = sys.argv[1]
else:
    comment = ''

def signal_handler(signal, frame):
    global data
    """After pressing ctrl-C to quit, this function will first run"""
    data.lj.set_dc_voltage2(0)
    print 'quitting'
    sys.exit(0)

def start():
    global path, filename, comment, data
    signal.signal(signal.SIGINT, signal_handler)

    if not os.path.exists(path):
        os.makedirs(path)
    
    data = cap.data_file(path, filename, freqs_to_sweep, comment, lj_chs=[1])
    data.dcbias(dcbias_setting)
    data.bridge.set_voltage(meas_volt)
    data.bridge.set_ave(ave_time_setting)
    #freqs_to_sweep = [20000]
    #freqs_to_sweep = [10000, 1000]

    #max_bias = 100.
    #bias_step = 20.
    dc_bias_values = np.arange(0, max_bias+bias_step, bias_step)
    dc_bias_values = np.concatenate((dc_bias_values, dc_bias_values[::-1]))
    dc_bias_values = np.concatenate((dc_bias_values, -dc_bias_values))
    #dc_bias_values = [0, 20, 40, 60, 80, 100, 120, 140]
    #dc_bias_values = [150]
    #data.dc_bias_measurement(freqs_to_sweep, 3, dc_bias_values, amp=50)
    #temp = data.ls.get_temp('A')
    #while temp > 85.1:
    #    print temp
    #    time.sleep(10)
    #    temp = data.ls.get_temp('A')
    ii = 0
    while True:
    #for ii in xrange(3):
        ii += 1
        print '\n\n......measurement set: %d...........\n\n' % ii
        data.dc_bias_measurement(freqs_to_sweep, measurements_per_volt, dc_bias_values, amp=amplification, offset=offset)

start()