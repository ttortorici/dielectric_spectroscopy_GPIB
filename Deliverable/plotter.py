import numpy as np
import os
import plotting_tool as plt


#Plotting limits
temp_range1 = [0, 120, 30]
cap_range = [1.22, 1.27, 0.02]
#cap_range = None
loss_range = [0, 0.004, .001]

#File to plot
# filepath = 'Deliverable/GBA120/2017-03-08'
# filenames = ['Cooling_1489003015_15.csv']
sample = 'GBA141'
date = '2016-07-22'
filepath = '%s/%s' % (sample, date)
filenames = ['Cooling_1469206296_6.csv']

#Plotting limits
"""temp_range1 = [0, 120, 30]
cap_range = [1.24, 1.33, 0.02]
loss_range = [0, 0.008, .002]

#File to plot
# filepath = 'Deliverable/GBA120/2017-03-08'
# filenames = ['Cooling_1489003015_15.csv']
sample = 'GBA124'
date = '2016-07-19'
filepath = '%s/%s' % (sample, date)
filenames = ['Cooling_1468959484_96.csv']"""

"""set units for time plot"""
time_axis = 'hr'


def load_data(file_path, file_names):
    print os.path.join(file_path, file_names[0])
    # all this skip nonsense is a work around so the code will ignore "empty" files
    skip = 0
    temp_skip = -1
    while not skip == temp_skip:    # as long as the "try" passes, the while loop dies
        temp_skip = skip
        try:
            data = np.loadtxt(os.path.join(file_path, file_names[0]), comments='#', delimiter=',', skiprows=4)
        except StopIteration:
            skip += 1
    if len(file_names) > 1:
        for ii, f in enumerate(file_names[1:]):
            try:
                data_temp = np.loadtxt(os.path.join(file_path, f), comments='#', delimiter=',', skiprows=4)
                try:
                    data = np.append(data, data_temp, axis=0)
                except ValueError:
                    data = np.append(data, np.array([data_temp]), axis=0)
            except StopIteration:
                pass
    return data

if 'min' in time_axis.lower():
    time_factor = 60
elif 'hr' in time_axis.lower():
    time_factor = 60 * 60
else:
    time_axis = 'min'
    time_factor = 60

data = load_data(filepath, filenames)
print np.shape(data)

timestamps = (data[:, 0] - data[0, 0]) / time_factor
temperature1 = data[:, 1]
temperature2 = data[:, 2]
freqs = data[:, 3]
capacitance = data[:, 4]
loss = data[:, 5]

titles = ['Capacitance vs Temperature %s %s', 'Loss vs Temperature %s %s']
ranges = [cap_range, loss_range]
axis_labels = [['T (K)', 'C (pF)'], ['T (K)', r'tan($\delta$)']]
datas = [capacitance, loss]
temp_ranges = [temp_range1, [0, 300, 100]]
sizes = ['small', 'big']

for title, range, axis_label, d in zip(titles, ranges, axis_labels, datas):
    for temp_range, size in zip(temp_ranges, sizes):
        p = plt.Plot(title % (sample, size), axis_label)
        p.plot_sep_freq(temperature1, d, freqs, temp_range, range)
        p.save(filepath)
p = plt.Plot('Fits on Peaks', ['T (K)', r'tan($\delta$)'])
p.plot_peaks(temperature1, loss, freqs)
p.save(filepath)
b = plt.Barrier_analysis(temperature1, loss, freqs)
b.plot()
b.p.save(filepath)
print 'barier height in kcal/mol is: ' + str(b.E_B/503.22) + ' +/- ' #+ str(b.pcov[0, 0]**2/503.22)
print 'tau0 is: ' + str(b.tau0) + ' +/- ' #+ str(b.pcov[1, 1]**2)
print 'temperature peaks are at: ' + str(b.temp_peak)
print 'error: ' #+ str(np.sqrt(np.diag(b.pcov)))

plt.show()