"""
Live plotting on Windows
Teddy 2017
"""
import sys
import Tkinter
import tkMessageBox
import matplotlib.pylab as plt
import calendar
import itertools
import data_files
import os
import csv
import time
import datetime
import numpy as np
import yaml
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
import DateAxisItem
import sys, time, os
pg.setConfigOption('background','w')
pg.setConfigOption('foreground','k')
sys.path.append('../GPIB')
import get


#cap_str_low = '1.68'
#cap_str_high = '1.74'


class Setup_Window(Tkinter.Tk):

    FONT_SIZE = 10
    FONT = 'Arial'

    time_axis = 'hr'
    titles = ['Capacitance vs Time',
              'Capacitance vs Temperature',
              'Loss vs Time',
              'Loss vs Temperature',
              'Capacitance and Loss vs Time',
              'Capacitance and Loss vs Temperature',
              'Log2 omega vs inverse T of Loss Peak']
    axes_labelss = [['Time [%s]' % time_axis, 'Capacitance [pF]', 'Temperature [K]'],
                    ['Temperature [K]', 'Capacitance [pF]'],
                    ['Time [%s]' % time_axis, 'Loss Tangent', 'Temperature [K]'],
                    ['Temperature [K]', 'Loss Tangent'],
                    ['Time [%s]' % time_axis, 'Loss Tangent', 'Capacitance [pF]'],
                    ['Temperature [K]', 'Loss Tangent', 'Capacitance [pF]'],
                    ['1/T [1/K]', 'Log2(omega)']]
    legend_locs = ['best', 'best', 'best', 'best', 'best', 'best', 'best']
    plot_ranges = [[False, False], [False], [False, False], [False], [False, False], [False, False], [False, False]]
    start_trim = 0
    end_trim = None
    time_trims = [[start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim]]

    def __init__(self):
        """Initialize"""
        """determine time factor"""
        if 'min' in Setup_Window.time_axis.lower():
            self.time_factor = 60
        elif 'hr' in Setup_Window.time_axis.lower():
            self.time_factor = 60 * 60
        else:
            raise ValueError('Setup_Window.time_axis has an invalid value')

        """establish the day data is getting taken"""
        date = str(datetime.date.today()).split('-')
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]

        """replace date with sys.argv entry"""
        if len(sys.argv) >= 2:
            datemsg = sys.argv[1].split('-')
            if len(datemsg) == 2:
                self.month = datemsg[0]
                self.day = datemsg[1]
            elif len(datemsg) == 3:
                self.year = datemsg[2]
                self.month = datemsg[0]
                self.day = datemsg[1]
            elif len(datemsg) == 1:
                try:
                    day_temp = int(datemsg[0])
                    if day_temp > int(self.day):
                        self.month = str(int(self.month) - 1)
                        if int(self.month) == 0:
                            self.month = '12'
                    self.day = datemsg[0]
                except ValueError:
                    pass

        """make sure the numbers come out right"""
        if len(self.day) == 1:
            self.day = '0' + self.day
        if len(self.month) == 1:
            self.month = '0' + self.month
        if len(self.year) == 2:
            self.year = '20' + self.year

        """get filepath in googledrive"""
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
        self.path = os.path.join(self.base_path, self.year, self.month, self.day)

        """get list of files in this directory"""
        filenames = data_files.file_name(self.month, self.day, self.year)
        self.filenames = []
        for f in filenames[0]:
            if not '_sorted' in f.lower():
                self.filenames.append(f)
        print 'All the files in the directory: ' + str(self.filenames)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('Plot Present 4')

        Tkinter.Label(self, text='Select the files you would like to plot:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=0, column=0, sticky=Tkinter.W)

        # Get presets
        with open(os.path.join(self.base_path, 'presets_plotting.yml'), 'r') as f:
            preset = yaml.load(f)
        cap_str_low = preset['cap'][0]
        cap_str_high = preset['cap'][1]
        loss_str_low = preset['loss'][0]
        loss_str_high = preset['loss'][1]

        """place checkbox list"""
        self.var_list = [0] * len(self.filenames)
        check_list = [0] * len(self.filenames)
        for ii, f in enumerate(self.filenames):
            comment = self.get_comment(f)       # grab comment from the file
            flength = self.count_rows(f)        # determine number of rows in file
            Tkinter.Label(self, text=comment,
                          font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=ii+1, column=0, sticky=Tkinter.W)
            self.var_list[ii] = Tkinter.IntVar()
            Tkinter.Checkbutton(self, text='%d rows in file' % flength,
                                variable=self.var_list[ii]).grid(row=ii+1, column=1, sticky=Tkinter.E + Tkinter.W)
            if len(self.var_list) == len(preset['files']):
                self.var_list[ii].set(preset['files'][ii])
            else:
                self.var_list[ii].set(1)

        next_row = len(self.filenames) + 1

        """Set Capacitance plotting range"""
        Tkinter.Label(self, text='Capacitance Range [pF]:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=next_row, column=1,
                                                                             sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_low = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_range_entry_low.grid(row=next_row, column=2, sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_low.insert(0, cap_str_low)
        self.cap_range_entry_high = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_range_entry_high.grid(row=next_row, column=3, sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_high.insert(0, cap_str_high)

        next_row += 1

        """Set Loss plotting range"""
        Tkinter.Label(self, text='Loss Tangent range:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=next_row, column=1,
                                                                             sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_low = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.loss_range_entry_low.grid(row=next_row, column=2, sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_low.insert(0, loss_str_low)
        self.loss_range_entry_high = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.loss_range_entry_high.grid(row=next_row, column=3, sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_high.insert(0, loss_str_high)

        next_row += 1

        self.plot_bool_list = [0] * len(Setup_Window.titles)
        for ii, title in enumerate(Setup_Window.titles):
            self.plot_bool_list[ii] = Tkinter.IntVar()
            Tkinter.Checkbutton(self, text=title,
                                variable=self.plot_bool_list[ii]).grid(row=next_row+ii, column=1,
                                                                       sticky=Tkinter.E + Tkinter.W)
            self.plot_bool_list[ii].set(preset['plot'][ii])

        next_row += ii+1

        """Create and place buttons"""
        Tkinter.Button(self, text="Go",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.go).grid(row=next_row, column=1, sticky=Tkinter.E + Tkinter.W)
        next_row += 1
        Tkinter.Label(self, text="2017 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=next_row, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.cleanUp)

        self.attributes('-topmost', True)

    def go(self):
        self.files_to_use = []
        bool_list = []
        for ii, var in enumerate(self.var_list):
            file_bool = var.get()
            bool_list.append(file_bool)
            if file_bool:
                self.files_to_use.append(self.filenames[ii])
        plot_bool_list = []
        for ii, var in enumerate(self.plot_bool_list):
            plot_bool = var.get()
            plot_bool_list.append(plot_bool)
        print plot_bool_list


        print "These files were selected: " + str(self.files_to_use)
        self.cap_range = [float(self.cap_range_entry_low.get()), float(self.cap_range_entry_high.get())]
        self.loss_range = [float(self.loss_range_entry_low.get()), float(self.loss_range_entry_high.get())]

        presets = {'files': bool_list,
                   'plot': plot_bool_list,
                   'cap': self.cap_range,
                   'loss': self.loss_range}

        with open(os.path.join(self.base_path, 'presets_plotting.yml'), 'w') as f:
            yaml.dump(presets, f)

        self.load_data()

        self.cleanUp()
        plot_bool_list = [bool(ii) for ii in plot_bool_list]
        titles = [title for ii, title in enumerate(Setup_Window.titles) if plot_bool_list[ii]]
        axes_labelss = [axes_labels for ii, axes_labels in enumerate(Setup_Window.axes_labelss) if plot_bool_list[ii]]
        time_trims = [time_trim for ii, time_trim in enumerate(Setup_Window.time_trims) if plot_bool_list[ii]]
        legend_locs = [legend_loc for ii, legend_loc in enumerate(Setup_Window.legend_locs) if plot_bool_list[ii]]
        plot_ranges = [plot_range for ii, plot_range in enumerate(Setup_Window.plot_ranges) if plot_bool_list[ii]]

        for title, axes_labels, time_trim, legend_loc, plot_range in zip(titles,
                                                                         axes_labelss,
                                                                         time_trims,
                                                                         legend_locs,
                                                                         plot_ranges):
            p = Plot(title, axes_labels, time_trim, legend_loc, plot_range)
            if title == 'Capacitance vs Time':
                p.plot_sep_freq(self.timestamps, self.capacitance, self.freqs, self.cap_range)
                p.plot(self.timestamps, self.temperature1, plot_range[1],
                       marker='r--', label='Stage A Temperature', ax='R')
                p.plot(self.timestamps, self.temperature2, plot_range[1],
                       marker='b--', label='Stage B Temperature', ax='R')
            elif title == 'Capacitance vs Temperature':
                p.plot_sep_freq(self.temperature1, self.capacitance,
                                self.freqs, self.cap_range)
            elif title == 'Loss vs Time':
                p.plot_sep_freq(self.timestamps, self.loss, self.freqs, self.loss_range)
                p.plot(self.timestamps, self.temperature1, plot_range[1],
                       marker='r--', label='Stage A Temperature', ax='R')
                p.plot(self.timestamps, self.temperature2, plot_range[1],
                       marker='b--', label='Stage B Temperature', ax='R')
            elif title == 'Loss vs Temperature':
                p.plot_sep_freq(self.temperature1, self.loss, self.freqs, self.loss_range)
            elif title == 'Capacitance and Loss vs Time':
                p.plot_sep_freq(self.timestamps, self.capacitance, self.freqs, self.cap_range,
                                label='Capacitance', ax='R')
                p.plot_sep_freq(self.timestamps, self.loss, self.freqs, self.loss_range, label='Loss')
            elif title == 'Capacitance and Loss vs Temperature':
                p.plot_sep_freq(self.temperature1, self.capacitance, self.freqs, self.cap_range,
                                label='Capicatance', ax='R')
                p.plot_sep_freq(self.temperature1, self.loss, self.freqs, self.loss_range, label='Loss')

            m = self.month + '_'
            path_to_save = os.path.join(get.googledrive(), 'Dielectric_data', 'Graphs', self.year,
                                        m + calendar.month_name[int(self.month)],
                                        self.day)

            plt.legend(loc=legend_loc)

            if not os.path.exists(path_to_save):
                os.makedirs(path_to_save)

            plt.savefig(os.path.join(path_to_save, title),
                        dpi=None, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches=None, pad_inches=0.1,
                        frameon=None)
        plt.show()


    def cleanUp(self):
        """Close window"""
        self.destroy()

    def get_comment(self, f):
        """Retrieve data file's comment"""
        with open(os.path.join(self.path, f), 'r') as ff:
            comment_list = next(itertools.islice(csv.reader(ff), 1, None))[0].strip('# ').split('... ')
        comment = comment_list[0]
        for c in comment_list[-1:]:
            comment += '; %s' % c
        return comment

    def count_rows(self, f):
        """Return the number of rows in a file"""
        return sum(1 for line in open(os.path.join(self.path, f), 'r'))

    def load_data(self):
        """Load the selected data files"""
        # all this skip nonsense is a work around so the code will ignore "empty" files
        skip = 0
        temp_skip = -1
        while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
            temp_skip = skip
            try:
                data = np.loadtxt(os.path.join(self.path, self.files_to_use[0]),
                                  comments='#', delimiter=',', skiprows=4)
            except StopIteration:
                skip += 1
        if len(self.files_to_use) > 1:
            for ii, f in enumerate(self.files_to_use[1:]):
                try:
                    data_temp = np.loadtxt(os.path.join(self.path, f), comments='#', delimiter=',', skiprows=4)
                    try:
                        data = np.append(data, data_temp, axis=0)
                    except ValueError:
                        data = np.append(data, np.array([data_temp]), axis=0)
                except StopIteration:
                    pass
        self.timestamps = (data[:, 0] - data[0, 0]) / self.time_factor
        self.temperature1 = data[:, 1]
        self.temperature2 = data[:, 2]
        self.freqs = data[:, 3]
        self.capacitance = data[:, 4]
        self.loss = data[:, 5]


class Plot:

    font = {'size': 20, 'color': 'k'}

    def __init__(self, title, axes_labels, time_trim, legend_loc, plot_range):
        self.title = title
        self.axes_labels = axes_labels
        self.time_trim = time_trim
        self.legend_loc = legend_loc
        self.plot_range = plot_range

        plot_ratio = np.array([6, 4])
        if 'linux' in sys.platform:
            plot_ratio[0] += 0.5
        plot_size = plot_ratio * 1.8

        self.fig, self.axL = plt.subplots()
        self.fig.set_size_inches(plot_size[0], plot_size[1], forward=True)

        self.fig.suptitle(self.title, fontsize=Plot.font['size'])

        # set axes labels
        self.axL.set_xlabel(axes_labels[0], fontsize=Plot.font['size'], color=Plot.font['color'])
        self.axL.set_ylabel(axes_labels[1], fontsize=Plot.font['size'], color=Plot.font['color'])

        # edit tick labels
        for tl in self.axL.get_yticklabels():
            tl.set_color(Plot.font['color'])
            tl.set_fontsize(Plot.font['size'])

        for tl in self.axL.get_xticklabels():
            tl.set_color(Plot.font['color'])
            tl.set_fontsize(Plot.font['size'])

        # generate 2nd y axis if 3 axes_labels given
        if len(axes_labels) > 2:
            self.axR = self.axL.twinx()
            self.axR.set_ylabel(axes_labels[2], fontsize=Plot.font['size'], color=Plot.font['color'])
            for tl in self.axR.get_yticklabels():
                tl.set_color(Plot.font['color'])
                tl.set_fontsize(Plot.font['size'])
                self.axR.get_yaxis().get_major_formatter().set_useOffset(False)
        self.axL.get_xaxis().get_major_formatter().set_useOffset(False)
        self.axL.get_yaxis().get_major_formatter().set_useOffset(False)

        plt.tight_layout()
        self.fig.subplots_adjust(top=0.9)

        # turn on grid lines
        self.axL.grid(True)

        ticklines = self.axL.get_xticklines() + self.axL.get_yticklines()
        gridlines = self.axL.get_xgridlines() + self.axL.get_ygridlines()

        for line in ticklines:
            line.set_linewidth(3)

        for line in gridlines:
            line.set_linestyle('-')

    def plot(self, x, y, plot_range=None, marker='b-', label='', ax='L'):
        """Plots y vs x; marker: search 'pyplot.plot' at http://matplotlib.org/api/pyplot_api.html"""
        if 'L' in ax.upper():
            self.axL.plot(x, y, marker, label=label, linewidth=3)
            if plot_range:
                self.axL.set_ylim(plot_range)
            if len(self.axes_labels) == 3:
                print label
                print x[0]
                print y[2]
                self.axR.plot(x[0], y[2], marker, label=label, linewidth=3)
        elif 'R' in ax.upper():
            self.axR.plot(x, y, marker, label=label, linewidth=3)
            if plot_range:
                self.axR.set_ylim(plot_range)

    def plot_sep_freq(self, x, y, freqs, plot_range, label='', ax='L'):
        """plot something separating frequencies"""
        frequencies_unique = np.sort(np.unique(freqs))
        if frequencies_unique[0] == -1:
            frequencies_unique = np.delete(frequencies_unique, 0)
        if 'L' in ax.upper():
            if len(frequencies_unique) <= 3:
                pen = ['k-', 'r-', 'b-']
            elif len(frequencies_unique) <= 6:
                pen = ['k-', 'k-.', 'r-', 'm-', 'b-', 'c-']
            elif len(frequencies_unique) <= 9:
                pen = ['k-', 'k-.', 'k:', 'r-', 'm-', 'y-', 'b-', 'c-', 'g-']
                # pen = ['ko', 'ro', 'bo', 'mo', 'yo', 'go']
        elif 'R' in ax.upper():
            if len(frequencies_unique) <= 3:
                pen = ['k--', 'r--', 'b--']
            elif len(frequencies_unique) <= 6:
                pen = ['k--', 'k_', 'r--', 'm--', 'b--', 'c--']
            elif len(frequencies_unique) <= 9:
                pen = ['k--', 'k+', 'k2', 'r--', 'm--', 'y--', 'b--', 'c--', 'g--']
                # pen = ['kv', 'rv', 'bv', 'mv', 'yv', 'gv']
        freq_locs = {}
        for freq in frequencies_unique:
            freq_locs[str(freq)] = np.where(freqs == freq)
        for ii, freq in enumerate(frequencies_unique):
            self.plot(x[freq_locs[str(freq)]], y[freq_locs[str(freq)]], plot_range=plot_range,
                      marker=pen[ii], label='%s %d Hz' % (label, freq), ax=ax)

if __name__ == '__main__':
    Setup_Window().mainloop()