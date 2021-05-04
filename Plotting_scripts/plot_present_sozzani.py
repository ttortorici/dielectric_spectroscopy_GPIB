"""Code for plotting presentation quality plots"""

import numpy as np
import matplotlib.pylab as plt
import data_files
import os
import datetime
import calendar
from matplotlib.pylab import rcParams
import sys;
sys.path.append('../GPIB')
import get


date = str(datetime.date.today()).split('-')
year = int(date[0])
month = int(date[1])
day = int(date[2])

# input parameters for easy tweaking
# bounds for good data
scrub = True
cap_bounds = [1.2, 1.2539]
loss_bounds = [0, 0.1]
temp_bounds = [6, 410]

# where to cut off time plot
start_time = 0
end_time = None

start_temp = 120
end_temp = 410


time_axis = 'hr'

if 'min' in time_axis.lower():
    time_factor = 60
elif 'hr' in time_axis.lower():
    time_factor = 60 * 60
else:
    time_axis = 'min'
    time_factor = 60

# store inputs
titles = ['Capacitance vs Time',
          'Capacitance vs Temperature',
          'Loss vs Time',
          'Loss vs Temperature',
          'Capacitance and Loss vs Time',
          'Capacitance and Loss vs Temperature']
axes_labelss = [['Time [%s]' % time_axis, 'Capacitance [pF]', 'Temperature [K]'],
                ['Temperature [K]', 'Capacitance [pF]'],
                ['Time [%s]' % time_axis, 'Loss Tangent', 'Temperature [K]'],
                ['Temperature [K]', 'Loss Tangent'],
                ['Time [%s]' % time_axis, 'Loss Tangent', 'Capacitance [pF]'],
                ['Temperature [K]', 'Loss Tangent', 'Capacitance [pF]']]
#legend_locs = [0, 2, 0, 2, 0, 2]
legend_locs = ['best', 'best', 'best', 'best', 'best', 'best']

plot_ranges = [[False, False], [False], [False, False], [False], [False, False], [False, False]]
#plot_ranges = [[[start_cap, end_cap], [start_temp, end_temp]],
#               [[start_cap, end_cap]],
#               [[start_loss, end_loss], [start_temp, end_temp]],
#               [[start_loss, end_loss]],
#               [[start_cap, end_cap], [start_loss, end_loss]],
#               [[start_cap, end_cap], [start_loss, end_loss]]]


if len(sys.argv) >= 2:
    datemsg = sys.argv[1].split('-')
    if len(datemsg) == 2:
        month = int(datemsg[0])
        day = int(datemsg[1])
    elif len(datemsg) == 3:
        year = int(datemsg[2])
        month = int(datemsg[0])
        day = int(datemsg[1])
    elif len(datemsg) == 1:
        try:
            day = int(datemsg[0])
        except ValueError:
            pass
if len(sys.argv) >= 3:
    try:
        timemsg = sys.argv[2].strip('[').strip(']').split(',')
        start_time = timemsg[0]
        end_time = timemsg[1]
    except IndexError:
        pass
if len(sys.argv) >= 4:
    if sys.argv[3].lower() == 'off':
        scrub = False
    else:
        scrub = True
        scrubmsg = sys.argv[3].strip('[').strip(']').split(',')
        cap_bounds = [scrubmsg[0], scrubmsg[1]]
        loss_bounds = [scrubmsg[2], scrubmsg[3]]


def load_data(file_path, file_names, scrub=True, cap_bounds=[1.2, 1.3], loss_bounds=[-0.5, 1]):
    data = np.loadtxt(os.path.join(file_path, file_names[0]), comments='#', delimiter=',', skiprows=3)
    if len(file_names) > 1:
        for ii, f in enumerate(file_names[1:]):
            data_temp = np.loadtxt(os.path.join(file_path, f), comments='#', delimiter=',', skiprows=3)
            try:
                data = np.append(data, data_temp, axis=0)
            except ValueError:
                data = np.append(data, np.array([data_temp]), axis=0)
    if scrub:
        data = scrub_data(data, cap_bounds, loss_bounds)
    return data


def scrub_data(data_old, cap_bounds=[1.2, 1.3], loss_bounds=[-0.5, 1]):
    cap_bounds = sorted(cap_bounds)
    loss_bounds = sorted(loss_bounds)
    # print np.shape(data_old)
    good_cap_data = np.where(np.logical_and(data_old[:, 4] > cap_bounds[0], data_old[:, 4] <= cap_bounds[1]))
    data_temp = data_old[good_cap_data]
    # print np.shape(data_temp)
    good_loss_data = np.where(np.logical_and(data_temp[:, 5] > loss_bounds[0], data_temp[:, 5] <= loss_bounds[1]))
    data_temp2 = data_temp[good_loss_data]
    # print np.shape(data_new)
    good_temper_data = np.where(np.logical_and(data_temp2[:, 1] > temp_bounds[0], data_temp2[:, 1] <= temp_bounds[1]))
    data_new = data_temp2[good_temper_data]
    return data_new


def plot(x, y, plot_range=None, marker='b-', label='', ax='L'):
    """Plots y vs x; marker: search 'pyplot.plot' at http://matplotlib.org/api/pyplot_api.html"""
    plot_num = len(plotlist)
    if 'L' in ax.upper():
        #plot_num = len(plotlistL)
        p, = axL.plot(x, y, marker, label=label, linewidth=3)
        if plot_range:
            axL.ylim(plot_range)
        #plotlistL.append(p)
        if len(axes_labels) == 3:
            if 'cap' in axes_labels[2].lower():
                z = [capacitance[20]]
            elif 'temp' in axes_labels[2].lower():
                z = [temperature1[20]]
            if 'time' in axes_labels[0].lower():
                w = [timestamps[0]]
            elif 'temp' in axes_labels[0].lower():
                w = [temperature1[0]]
            # print z
            axR.plot(w, z, marker, label=label, linewidth=3)
    elif 'R' in ax.upper():
        #plot_num = len(plotlistR)
        p, = axR.plot(x, y, marker, label=label, linewidth=3)
        if plot_range:
            axL.ylim(plot_range)
        #plotlistR.append(p)
    plotlist.append(p)


def plot_sep_freq(x, y, freqs, plot_range, label='', ax='L'):
    """plot something separating frequencies"""
    if 'L' in ax.upper():
        #pen = ['k-', 'r-', 'b-', 'm-', 'y-', 'g-']
        pen = ['ko', 'ro', 'bo', 'mo', 'yo', 'go']
    elif 'R' in ax.upper():
        #pen = ['k--', 'r--', 'b--', 'm--', 'y--', 'g--']
        pen = ['kv', 'rv', 'bv', 'mv', 'yv', 'gv']
    frequencies_unique = np.sort(np.unique(freqs))
    freq_locs = {}
    for freq in frequencies_unique:
        freq_locs[str(freq)] = np.where(freqs == freq)
    for ii, freq in enumerate(frequencies_unique):
        #if 'L' in ax:
        #    plot_num = len(plotlistL)
        #elif 'R' in ax:
        #    plot_num = len(plotlistR)
        plot_num = len(plotlist)
        plot(x[freq_locs[str(freq)]], y[freq_locs[str(freq)]], plot_range=plot_range,
             marker=pen[ii], label='%s %d Hz' % (label, freq), ax=ax)
        #if 'L' in ax:
        #    plotlistL[plot_num].freqs = freqs
        #elif 'R' in ax:
        #    plotlistR[plot_num].freqs = freqs


filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
filenames = [[#'Cooling_1467046825_62.csv',
              'Cooling_1467047885_55.csv',      # data
              #'Cooling_1467087517_26.csv',
              'Cooling_1467096780_85.csv',      # overnight
              'Cooling_1467135489_32.csv',      # heating to 365 and cooling to liquid nitro
              #'Cooling_1467135489_33.csv'
              #'Cooling_1467159603_24.csv'
            ]]    # reproducing helium data

print filenames[0]

data = load_data(filepath, filenames[0], scrub, cap_bounds, loss_bounds)

timestamps = (data[:, 0] - data[0, 0]) / time_factor
temperature1 = data[:, 1]
temperature2 = data[:, 2]
freqs = data[:, 3]
capacitance = data[:, 4]
loss = data[:, 5]


#start_trim = np.argmax(timestamps > 0)
if end_time:
    end_trim = len(timestamps) - np.argmax(timestamps[::-1] < end_time)
else:
    end_trim = None
start_trim = start_time

#end_trim = None
time_trims = [[start_trim, end_trim],
         [start_trim, end_trim],
         [start_trim, end_trim],
         [start_trim, end_trim],
         [start_trim, end_trim],
         [start_trim, end_trim]]
plot_ratio = np.array([6, 4])
if 'linux' in sys.platform:
    plot_ratio[0] += 0.5
plot_size = plot_ratio*1.8
# if on mac, make plots bigger
# if sys.platform == 'darwin':
#     plot_size *= 1.75
rcParams['figure.figsize'] = plot_size[0], plot_size[1]

font = {'size': 20, 'color': 'k'}

# titles = titles[:1]
# axes_labelss = axes_labelss[:1]

for title, axes_labels, time_trim, legend_loc, plot_range in \
        zip(titles, axes_labelss, time_trims, legend_locs, plot_ranges):
    start_trim = int(time_trim[0])
    end_trim = time_trim[1]
    # generate graphic
    fig, axL = plt.subplots()
    fig.set_size_inches(plot_size[0], plot_size[1], forward=True)

    # set title
    fig.suptitle(title, fontsize=font['size'], color=font['color'])

    # set axes labels
    axL.set_xlabel(axes_labels[0], fontsize=font['size'], color=font['color'])
    axL.set_ylabel(axes_labels[1], fontsize=font['size'], color=font['color'])

    # edit tick labels
    for tl in axL.get_yticklabels():
        tl.set_color(font['color'])
        tl.set_fontsize(font['size'])

    for tl in axL.get_xticklabels():
        tl.set_color(font['color'])
        tl.set_fontsize(font['size'])

    # generate 2nd y axis if 3 axes_labels given
    if len(axes_labels) > 2:
        axR = axL.twinx()
        axR.set_ylabel(axes_labels[2], fontsize=font['size'], color=font['color'])
        for tl in axR.get_yticklabels():
            tl.set_color(font['color'])
            tl.set_fontsize(font['size'])

        axR.get_yaxis().get_major_formatter().set_useOffset(False)
    axL.get_xaxis().get_major_formatter().set_useOffset(False)
    axL.get_yaxis().get_major_formatter().set_useOffset(False)

    # seed plotlists
    #plotlistL = []
    #plotlistR = []
    plotlist = []

    if title == 'Capacitance vs Time':
        plot_sep_freq(timestamps[start_trim: end_trim], capacitance[start_trim: end_trim], freqs[start_trim: end_trim],
                      plot_range[0])
        plot(timestamps[start_trim: end_trim], temperature1[start_trim: end_trim], plot_range[1],
             marker='r--', label='Stage A Temperature', ax='R')
        plot(timestamps[start_trim: end_trim], temperature2[start_trim: end_trim], plot_range[1],
             marker='b--', label='Stage B Temperature', ax='R')
    elif title == 'Capacitance vs Temperature':
        plot_sep_freq(temperature1[start_trim: end_trim], capacitance[start_trim: end_trim],
                      freqs[start_trim: end_trim], plot_range[0])
    elif title == 'Loss vs Time':
        plot_sep_freq(timestamps[start_trim: end_trim], loss[start_trim: end_trim], freqs[start_trim: end_trim],
                      plot_range[0])
        plot(timestamps[start_trim: end_trim], temperature1[start_trim: end_trim], plot_range[1],
             marker='r--', label='Stage A Temperature', ax='R')
        plot(timestamps[start_trim: end_trim], temperature2[start_trim: end_trim], plot_range[1],
             marker='b--', label='Stage B Temperature', ax='R')
    elif title == 'Loss vs Temperature':
        plot_sep_freq(temperature1[start_trim: end_trim], loss[start_trim: end_trim], freqs[start_trim: end_trim],
                      plot_range[0])
    elif title == 'Capacitance and Loss vs Time':
        plot_sep_freq(timestamps[start_trim: end_trim], capacitance[start_trim: end_trim],
                      freqs[start_trim: end_trim], plot_range[0], label='Capacitance', ax='R')
        plot_sep_freq(timestamps[start_trim: end_trim], loss[start_trim: end_trim],
                      freqs[start_trim: end_trim], plot_range[1], label='Loss')
    elif title == 'Capacitance and Loss vs Temperature':
        plot_sep_freq(temperature1[start_trim: end_trim], capacitance[start_trim: end_trim],
                      freqs[start_trim: end_trim], plot_range[0], label='Capicatance', ax='R')
        plot_sep_freq(temperature1[start_trim: end_trim], loss[start_trim: end_trim],
                      freqs[start_trim: end_trim], plot_range[1], label='Loss')
    print title
    print axes_labels
    print time_trim
    print legend_loc

    if'linux' in sys.platform.lower():
        plt.legend(handles=plotlist, loc=legend_loc)
    else:
        plt.legend(loc=legend_loc)

    #turn on grid lines
    axL.grid(True)

    ticklines = axL.get_xticklines() + axL.get_yticklines()
    gridlines = axL.get_xgridlines() + axL.get_ygridlines()

    for line in ticklines:
        line.set_linewidth(3)

    for line in gridlines:
        line.set_linestyle('-')

    path_to_save = os.path.join(get.googledrive(), 'Dielectric_data', 'Graphs', str(year), calendar.month_name[month],
                                str(day))

    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    plt.savefig(os.path.join(path_to_save, title),
                dpi=None, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, bbox_inches=None, pad_inches=0.1,
                frameon=None)


plt.show()

