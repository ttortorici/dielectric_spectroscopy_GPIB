import capacitance_measurement_tools as cap
import signal
import sys
import os
import time
import datetime
import numpy as np
import sys
sys.path.append('../GPIB')
import get


date = str(datetime.date.today()).split('-')
year = date[0]
month = date[1]
day = date[2]
path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', year, month, day)
filename = 'Cooling_%s' % (str(time.time()).replace('.', '_'))
if len(sys.argv) > 1:
    comment = sys.argv[1]
else:
    comment = ''

def takeInput():
    """This function will be executed via thread"""
    value = raw_input("Press Enter to Pause")
    return value

def signal_handler(signal, frame):
    """After pressing ctrl-C to quit, this function will first run"""
    sort_by_separate_frequencies()
    print 'quitting'
    sys.exit(0)

def start():
    global path, filename, comment
    signal.signal(signal.SIGINT, signal_handler)

    if not os.path.exists(path):
        os.makedirs(path)
    data = cap.data_file(path, filename, comment)
    data.dcbias('LOW')
    data.lj.set_dc_voltage(-60., amp=100.)
    #data.dcbias('OFF')
    #freqs_to_sweep = [100, 400, 1000, 1400, 10000, 14000]
    freqs_to_sweep = [14000, 1400, 400]
    while True:
        for ii in xrange(10):
            data.sweep_freq(freqs_to_sweep, 1)
        #data.speak('Adjust probes')
        #print 'Adjust Probes'
        #raw_input("Press Enter to continue...")
    # data.cont_meas(1000)
    # data.sweep_heat(low=320, high=400, step_size=5, freqs=freqs_to_sweep, measure_per_freq=3, hold_time=60)

def load_data():
    """for loading data back in to sort at the end"""
    global path, filename
    print os.path.join(path, filename)
    if '.csv' in filename:
        f = filename
    else:
        f = filename + '.csv'
    data = np.loadtxt(os.path.join(path, f), comments='#', delimiter=',', skiprows=4)
    return data

def sort_by_separate_frequencies():
    global path, filename, comment
    """Load Data"""
    data_old = load_data()
    freqs = data_old[:, 3]
    """Determine unique frequencies used, x[freq_locs[str(freq)]] to call"""
    unique_frequencies = np.sort(np.unique(freqs))
    if unique_frequencies[0] == -1:
        unique_frequencies = np.delete(unique_frequencies, 0)
    freq_locs = {}
    timestamps = {}
    temperature1 = {}
    temperature2 = {}
    capacitance = {}
    loss = {}
    length = {}
    voltage_rms = {}
    for freq in unique_frequencies:
        freq_locs[str(freq)] = np.where(freqs == freq)
        timestamps[str(freq)] = data_old[:, 0][freq_locs[str(freq)]]
        temperature1[str(freq)] = data_old[:, 1][freq_locs[str(freq)]]
        temperature2[str(freq)] = data_old[:, 2][freq_locs[str(freq)]]
        capacitance[str(freq)] = data_old[:, 4][freq_locs[str(freq)]]
        loss[str(freq)] = data_old[:, 5][freq_locs[str(freq)]]
        voltage_rms[str(freq)] = data_old[:, 6][freq_locs[str(freq)]]
        length[str(freq)] = len(timestamps[str(freq)])
    freq_with_most_data = max(length.iterkeys(), key=(lambda frequency: length[frequency]))
    """make sure all data sets are same length"""
    for freq in unique_frequencies:
        amount_to_append = length[freq_with_most_data] - length[str(freq)]
        for ii in xrange(amount_to_append):
            timestamps[str(freq)] = np.append(timestamps[str(freq)], -1)
            temperature1[str(freq)] = np.append(temperature1[str(freq)], -1)
            temperature2[str(freq)] = np.append(temperature2[str(freq)], -1)
            capacitance[str(freq)] = np.append(capacitance[str(freq)], -1)
            loss[str(freq)] = np.append(loss[str(freq)], -1)
            voltage_rms[str(freq)] = np.append(voltage_rms[str(freq)], -1)
    if '.csv' in filename:
        filename = filename[:-4]
    data_sorted = cap.data_file(path, filename + '_sorted',
                                comment + '... Frequencies: %dHz, %dHz, %dHz' % tuple(unique_frequencies))
    for ii in xrange(length[freq_with_most_data]):
        data_to_write = []
        for freq in unique_frequencies:
            data_to_write.append(timestamps[str(freq)][ii])
            data_to_write.append(temperature1[str(freq)][ii])
            data_to_write.append(temperature2[str(freq)][ii])
            data_to_write.append(capacitance[str(freq)][ii])
            data_to_write.append(loss[str(freq)][ii])
            data_to_write.append(voltage_rms[str(freq)][ii])
            data_to_write.append(int(freq))
        data_sorted.write_row2(data_to_write)
    print "... data sorted..."



    data_to_write = [time.time(), temperature1, temperature2, -1, -1, -1, -1]

if __name__ == "__main__":
    start()