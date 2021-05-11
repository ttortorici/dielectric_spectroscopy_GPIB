import sys
import os
import capacitance_measurement_tools as cap
import numpy as np
from builtins import input


def takeInput():
    """This function will be executed via thread"""
    value = input("Press Enter to Pause")
    return value


def signal_handler(signal, frame):
    """After pressing ctrl-C to quit, this function will first run"""
    sort_by_separate_frequencies()
    print('quitting')
    sys.exit(0)


def load_data(path, filename):
    """for loading data back in to sort at the end"""
    print(os.path.join(path, filename))
    if '.csv' in filename:
        f = filename
    else:
        f = filename + '.csv'
    data = np.loadtxt(os.path.join(path, f), comments='#', delimiter=',', skiprows=4)
    return data


def sort_by_separate_frequencies(path, filename, comment):
    """Load Data"""
    data_old = load_data(path, filename)
    freqs = data_old[:, 3]
    """Determine unique frequencies used, x[freq_locs[str(freq)]] to call"""
    unique_frequencies = np.sort(np.unique(freqs))[::-1]
    if unique_frequencies[0] == -1:
        unique_frequencies = np.delete(unique_frequencies, 0)
    unique_frequencies = list(unique_frequencies)
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
        for ii in range(amount_to_append):
            timestamps[str(freq)] = np.append(timestamps[str(freq)], -1)
            temperature1[str(freq)] = np.append(temperature1[str(freq)], -1)
            temperature2[str(freq)] = np.append(temperature2[str(freq)], -1)
            capacitance[str(freq)] = np.append(capacitance[str(freq)], -1)
            loss[str(freq)] = np.append(loss[str(freq)], -1)
            voltage_rms[str(freq)] = np.append(voltage_rms[str(freq)], -1)
    if '.csv' in filename:
        filename = filename[:-4]
    comment += '... Frequencies:'
    for freq in unique_frequencies:
        comment += ' %dHz' % freq
    print(tuple(unique_frequencies))
    data_sorted = cap.data_file(path, filename + '_sorted',
                                unique_freqs=unique_frequencies,
                                comment=comment + '... Frequencies: %dHz, %dHz, %dHz' % tuple(unique_frequencies),
                                sorter=True)
    for ii in range(length[freq_with_most_data]):
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
    print("... data sorted...")
