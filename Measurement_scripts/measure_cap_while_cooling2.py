import threading
try:
    import Tkinter
except ImportError:
    import tkinter as Tkinter
# import tkMessageBox
import capacitance_measurement_tools as cap
import signal
import sys
import data_sorter as ds
import os
import time
import datetime
import yaml
import numpy as np
import sys
sys.path.append('../GPIB')
import get
sys.path.append('..')
import sort_comments


class Setup_Window(Tkinter.Tk):

    FONT_SIZE = 10
    FONT = 'Arial'

    def __init__(self):
        # establish the day data is getting taken
        date = str(datetime.date.today()).split('-')
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]

        # get filepath in googledrive
        self.path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', self.year, self.month, self.day)

        # name file
        self.filename = 'Cooling_%s' % (str(time.time()).replace('.', '_'))

        # load presets
        """with open(os.path.join(self.path, 'comments.yml'), 'w') as f:
            preset = yaml.load(f, default_flow_style=False)"""

        # set up window
        Tkinter.Tk.__init__(self)
        self.title(self.filename)

        """
        create and place labels
        """
        Tkinter.Label(self, text='Please enter parameters then press "Go"',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=0, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="Capacitor Chip ID:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=1, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="Sample:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=2, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="Frequencies of measurement [in Hz, separate by commas]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=3, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="Measurement Voltage amplitude [in Volts RMS]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=4, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="AH Averaging Time [0-15]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=5, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="DC Bias Setting:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=6, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="DC Bias Value [0-100V]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=7, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="Amplification level on DC bias:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=8, column=0, sticky=Tkinter.W)
        Tkinter.Label(self, text="Purpose of measurement:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=9, column=0, sticky=Tkinter.W)

        """
        Create and place entry boxes
        """
        self.capchipID = ''
        self.capID = ''
        self.capchipID_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.capchipID_entry.grid(row=1, column=1, sticky=Tkinter.E + Tkinter.W)
        self.capID_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.capID_entry.grid(row=2, column=1, sticky=Tkinter.E + Tkinter.W)

        """
        Frequenies to measure
        """
        self.frequencies = [400, 1400, 12000]
        self.freq_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.freq_entry.grid(row=3, column=1, sticky=Tkinter.E + Tkinter.W)
        self.freq_entry.insert(0, str(self.frequencies).strip('[').strip(']'))

        """
        Measurement Voltage
        """
        self.meas_volt = 15
        self.volt_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.volt_entry.grid(row=4, column=1, sticky=Tkinter.E + Tkinter.W)
        self.volt_entry.insert(0, self.meas_volt)

        """
        Averaging time
        """
        self.ave_time_val = 0
        self.ave_time_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.ave_time_entry.grid(row=5, column=1, sticky=Tkinter.E + Tkinter.W)
        self.ave_time_entry.insert(0, self.ave_time_val)

        """
        set up DC select
        """
        self.dcbias = 'off'
        self.dcbias_selection = Tkinter.IntVar(self)
        self.dcbias_selection.set(0)

        Tkinter.Radiobutton(self, text="Off", variable=self.dcbias_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.dcselect).grid(row=6, column=1)
        Tkinter.Radiobutton(self, text="I-Low", variable=self.dcbias_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.dcselect).grid(row=6, column=2)
        Tkinter.Radiobutton(self, text="I-High", variable=self.dcbias_selection, value=2,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.dcselect).grid(row=6, column=3)

        """
        DC voltage value
        """
        self.dcbias_val = 0
        self.dcbias_val_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.dcbias_val_entry.grid(row=7, column=1, sticky=Tkinter.E + Tkinter.W)
        self.dcbias_val_entry.insert(0, self.dcbias_val)

        """
        Amplification level of DC voltage
        """
        self.amp_val = 100
        self.amp_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.amp_entry.grid(row=8, column=1, sticky=Tkinter.E + Tkinter.W)
        self.amp_entry.insert(0, self.amp_val)

        """
        Extra Comment
        """
        self.purpose_val = ''
        self.purpose_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.purpose_entry.grid(row=9, column=1, sticky=Tkinter.E + Tkinter.W)

        """Create and place buttons"""
        Tkinter.Button(self, text="Go",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.go).grid(row=10, column=1, sticky=Tkinter.E + Tkinter.W)
        Tkinter.Label(self, text="2017 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=11, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.cleanUp)

        self.attributes('-topmost', True)

    def dcselect(self):
        if self.dcbias_selection.get() == 0:
            self.dcbias = 'off'
            print('selected off')
        elif self.dcbias_selection.get() == 1:
            self.dcbias = 'low'
            print('selected low')
        elif self.dcbias_selection.get() == 2:
            self.dcbias = 'high'
            print('selected high')

    def go(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.capchipID = str(self.capchipID_entry.get())
        self.capID = str(self.capID_entry.get())
        self.frequencies = sorted([float(freq) for freq in str(self.freq_entry.get()).split(',')])[::-1]
        if len(self.frequencies) == 0:
            raise IOError('Invalid frequency input')
        self.meas_volt = abs(float(self.volt_entry.get()))
        if self.meas_volt > 15:
            self.meas_volt = 15
            print('Set voltage measurement to 15')
        self.ave_time_val = int(self.ave_time_entry.get())
        self.dcbias_val = float(self.dcbias_val_entry.get())
        self.amp_val = float(self.amp_entry.get())
        self.purpose_val = str(self.purpose_entry.get())
        print('Chip ID: ' + self.capchipID)
        print('Capacitor ID: ' + self.capID)
        print('Frequencies to measure: ' + str(self.frequencies) + 'Hz')
        print('Voltage of measurement: ' + str(self.meas_volt) + 'V')
        print('DC bias setting: ' + self.dcbias)
        print('DC bias set to: ' + str(self.dcbias_val) + 'V')
        print('Amplifier is: ' + str(self.amp_val) + 'x')
        print(self.purpose_val)

        self.cleanUp()

        #comment
        self.comment = 'Chip ID: %s... Sample: %s... %s' % (self.capchipID, self.capID, self.purpose_val)

        if not os.path.exists(self.path):
            os.makedirs(self.path)
        data = cap.data_file(self.path, self.filename, self.comment)
        data.dcbias(self.dcbias)
        data.bridge.set_voltage(self.meas_volt)
        data.bridge.set_ave(self.ave_time_val)
        #try:
        if 1:
            if abs(self.dcbias_val) > 15:
                step = 10 * np.sign(self.dcbias_val)
                for volt in np.arange(step, self.dcbias_val+step, step):
                    print('setting dc voltage to %d' % volt)
                    data.lj.set_dc_voltage2(volt, amp=self.amp_val)
                    time.sleep(2)
            else:
                print('setting dc voltage to %d' % self.dcbias_val)
                data.lj.set_dc_voltage(self.dcbias_val, amp=self.amp_val)
        #except:
        #    pass
        while True:
            for ii in range(10):
                data.sweep_freq(self.frequencies, 1)

    def cleanUp(self):
        self.destroy()

    def signal_handler(self, signal, frame):
        """After pressing ctrl-C to quit, this function will first run"""
        ds.sort_by_separate_frequencies(self.path, self.filename, self.comment)
        sort_comments.sort_comments()
        print('quitting')
        sys.exit(0)

def start():
    Setup_Window.mainloop()


if __name__ == '__main__':
    Setup_Window().mainloop()