"""Code for plotting presentation quality plots"""

import numpy as np
import matplotlib.pylab as plt

class SimplePlot:
    def __init__(self, plot_num, x, y, label, ax, freqs=None):
        self.plot_num = plot_num
        self.x = x
        self.y = y
        self.label = label
        self.ax = ax
        self.freqs = freqs

class Graph:
    def __init__(self, title, axes_labels=['', ''], font={'size': 16, 'color': 'k'}, plot_size=(400, 900)):
        # store inputs
        self.title = title
        self.axes_labels = axes_labels
        self.plot_size = plot_size
        self.font = font

        # generate graphic
        self.fig, self.axL = plt.subplots()
        self.fig.set_size_inches(plot_size[0], plot_size[1], forward=True)

        # set title
        self.fig.suptitle(title, fontsize=self.font['size'], color=self.font['color'])

        # set axes labels
        self.axL.set_xlabel(self.axes_labels[0], fontsize=self.font['size'], color=self.font['color'])
        self.axL.set_ylabel(self.axes_labels[1], fontsize=self.font['size'], color=self.font['color'])

        # edit tick labels
        for tl in self.axL.get_yticklabels():
            tl.set_color(self.font['color'])
            tl.set_fontsize(self.font['size'])

        # generate 2nd y axis if 3 axes_labels given
        if len(self.axes_labels) > 2:
            self.axR = self.axL.twinx()
            self.axR.set_ylabel(self.axes_labels[2], fontsize=self.font['size'], color=self.font['color'])
            for tl in self.axR.get_yticklabels():
                tl.set_color(self.font['color'])
                tl.set_fontsize(self.font['size'])

        # seed plotlists
        self.plotlistL = []
        self.plotlistR = []
        
    def plot(self, x, y, marker='b-', label='', ax='L'):
        """Plots y vs x; marker: search 'pyplot.plot' at http://matplotlib.org/api/pyplot_api.html"""
        if 'L' in ax.upper():
            plot_num = len(self.plotlistL)
            self.axL.plot(x, y, marker)
            p = SimplePlot(plot_num, x, y, label, ax)
            self.plotlistL.append(p)
        elif 'R' in ax.upper():
            plot_num = len(self.plotlistR)
            self.axR.plot(x, y, marker)
            p = SimplePlot(plot_num, x, y, label, ax)
            self.plotlistR.append(p)

    def plot_sep_freq(self, x, y, freqs, ax='L'):
        """plot something separating frequencies"""
        pen = ['k-', 'r-', 'b-']
        frequencies_unique = np.sort(np.unique(freqs))
        freq_locs = {}
        for freq in frequencies_unique:
            freq_locs[str(freq)] = np.where(freqs == freq)
        for ii, freq in enumerate(frequencies_unique):
            if 'L' in ax:
                plot_num = len(self.plotlistL)
            elif 'R' in ax:
                plot_num = len(self.plotlistR)
            self.plot(x[freq_locs[str(freq)]], y[freq_locs[str(freq)]], marker=pen[ii], label='%d Hz' % freq, ax=ax)
            if 'L' in ax:
                self.plotlistL[plot_num].freqs = freqs
            elif 'R' in ax:
                self.plotlistR[plot_num].freqs = freqs

    def grid(self, on=True):
        """Turn on grid lines"""
        self.axL.grid(on)

    def logx(self, on=True):
        """Make log scale on x axis"""
        if on:
            msg = 'log'
        else:
            msg = 'linear'
        self.axL.set_xscale(msg)
        self.axR.set_xscale(msg)

    def logy(self, on=True, ax=''):
        """Make log scale on y axis"""
        if on:
            msg = 'log'
        else:
            msg='linear'
        if 'L' in ax:
            self.axL.set_yscale(msg)
        elif 'R' in ax:
            self.axR.set_yscale(msg)
        else:
            try:
                self.axL.set_yscale(msg)
                self.axR.set_yscale(msg)
            except AttributeError:
                self.axL.set_yscale(msg)

    def loglog(self, on=True, ax=''):
        self.logx(on)
        self.logy(on, ax)

    #@staticmethod
    def show(self):
        """call to show plots"""
        print self.plotlistL
        plt.show()


def load_data(file_path, file_names):
    data = np.loadtxt(os.path.join(file_path, file_names[0]), comments='#', delimiter=',', skiprows=3)
    if len(file_names) > 1:
        for ii, f in enumerate(file_names[1:]):
            data_temp = np.loadtxt(os.path.join(file_path, f), comments='#', delimiter=',', skiprows=3)
            try:
                data = np.append(data, data_temp, axis=0)
            except ValueError:
                data = np.append(data, np.array([data_temp]), axis=0)
    data = scrub_data(data)
    return data


def scrub_data(data_old):
    good_cap_data = np.where(data_old[:, 4] > 1.2)
    data_temp = data_old[good_cap_data]
    good_loss_data = np.where(np.logical_and(data_temp[:, 5] > 0, data_temp[:, 5] <= 1))
    data_new = data_temp[good_loss_data]
    return data_new

def plot_ctime():
    Cap_v_time = Graph('Capacitance vs Time', ['Time [min]', 'Capacitance [pF]', 'Temperature [K]'])
    Cap_v_time.plot_sep_freq(timestamps, capacitance, freqs)
    Cap_v_time.plot(timestamps, temperature1, marker='r-.', label='Stage A Temperature', ax='R')
    Cap_v_time.plot(timestamps, temperature2, marker='b-.', label='Stage B Temperature', ax='R')
    Cap_v_time.show()

def plot_ctemp():
    Cap_v_temp = Graph('Capacitance vs Temperature', ['Temperature [K]', 'Capactiance [pF]'])
    Cap_v_temp.plot_sep_freq(temperature1, capacitance, freqs)
    Cap_v_temp.grid(True)
    Cap_v_temp.show()

def plot_ltemp():
    Loss_v_temp = Graph('Loss vs Temperature', ['Temperature [K]', 'Loss Tangent'])
    Loss_v_temp.plot_sep_freq(temperature1, loss, freqs)
    Loss_v_temp.logy(True)
    Loss_v_temp.grid(True)
    #Loss_v_temp.range(20, 400)
    Loss_v_temp.show()

if __name__ == '__main__':
    import data_files
    import os
    import datetime
    import sys;
    sys.path.append('../GPIB')
    import get

    date = str(datetime.date.today()).split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    if len(sys.argv) == 3:
        month = sys.argv[1]
        day = sys.argv[2]
    elif len(sys.argv) == 4:
        year = sys.argv[3]
        month = sys.argv[1]
        day = sys.argv[2]
    elif len(sys.argv) == 2:
        day = sys.argv[1]

    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    filenames = data_files.file_name(month, day, year)

    data = load_data(filepath, filenames[0])

    timestamps = (data[:, 0] - data[0, 0]) / 60
    temperature1 = data[:, 1]
    temperature2 = data[:, 2]
    freqs = data[:, 3]
    capacitance = data[:, 4]
    loss = data[:, 5]

    plot_ltemp()
