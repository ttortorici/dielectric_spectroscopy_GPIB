### do not use

import threading
import Tkinter
import tkMessageBox
import capacitance_measurement_tools as cap
import signal
import sys
import data_sorter as ds
import os
import time
import datetime
#import yaml
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
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
        self.path = os.path.join(self.base_path, self.year, self.month, self.day)

        # load presets
        with open(os.path.join(self.base_path, 'presets.yml'), 'r') as f:
            preset = yaml.load(f)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('Measure Capacitance')

        """
        create and place labels
        """
        r = 0
        Tkinter.Label(self, text='Please enter parameters then press "Go"',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text='File Title Header (optional)',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Capacitor Chip ID:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Sample:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Frequencies of measurement [in Hz, separate by commas]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Measurement Voltage amplitude [in Volts RMS]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="AH Averaging Time [0-15]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="DC Bias Setting:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="DC Bias Value [0-100V]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Amplification level on DC bias:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Purpose of measurement:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)

        """
        Create and place entry boxes
        """
        r = 1
        
        self.title = preset['title']
        self.title_entry = Tkinter. Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.title_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.title_entry.insert(0, self.title)
        
        self.capchipID = preset['id']
        self.capID = preset['sample']
        self.capchipID_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.capchipID_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.capchipID_entry.insert(0, self.capchipID)
        self.capID_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.capID_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.capID_entry.insert(0, self.capID)

        """
        Frequenies to measure
        """
        self.frequencies = preset['freqs']
        self.freq_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.freq_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.freq_entry.insert(0, str(self.frequencies).strip('[').strip(']'))

        """
        Measurement Voltage
        """
        self.meas_volt = preset['v']
        self.volt_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.volt_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.volt_entry.insert(0, self.meas_volt)

        """
        Averaging time
        """
        self.ave_time_val = preset['ave']
        self.ave_time_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.ave_time_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.ave_time_entry.insert(0, self.ave_time_val)

        """
        set up DC select
        """
        self.dcbias = preset['dc']
        print self.dcbias
        self.dcbias_selection = Tkinter.IntVar(self)
        dc_setting = {'off': 0,
                      'low': 1,
                      'high': 2}
        self.dcbias_selection.set(dc_setting[self.dcbias])

        Tkinter.Radiobutton(self, text="Off", variable=self.dcbias_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.dcselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="I-Low", variable=self.dcbias_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.dcselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="I-High", variable=self.dcbias_selection, value=2,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.dcselect).grid(row=r, column=3)
        r += 1

        """
        DC voltage value
        """
        self.dcbias_val = preset['dcv']
        self.dcbias_val_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.dcbias_val_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.dcbias_val_entry.insert(0, self.dcbias_val)

        """
        Amplification level of DC voltage
        """
        self.amp_val = preset['amp']
        self.amp_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.amp_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.amp_entry.insert(0, self.amp_val)

        """
        Extra Comment
        """
        self.purpose_val = preset['purp']
        self.purpose_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.purpose_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.purpose_entry.insert(0, self.purpose_val)
        r += 1

        """Create and place buttons"""
        Tkinter.Button(self, text="Go",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.go).grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        Tkinter.Label(self, text="2017 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.cleanUp)

        self.attributes('-topmost', True)

    def dcselect(self):
        if self.dcbias_selection.get() == 0:
            self.dcbias = 'off'
            print 'selected off'
        elif self.dcbias_selection.get() == 1:
            self.dcbias = 'low'
            print 'selected low'
        elif self.dcbias_selection.get() == 2:
            self.dcbias = 'high'
            print 'selected high'

    def go(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.title = str(self.title_entry.get())
        self.capchipID = str(self.capchipID_entry.get())
        self.capID = str(self.capID_entry.get())
        self.frequencies = sorted([float(freq) for freq in str(self.freq_entry.get()).split(',')])[::-1]
        if len(self.frequencies) == 0:
            raise IOError('Invalid frequency input')
        self.meas_volt = abs(float(self.volt_entry.get()))
        if self.meas_volt > 15:
            self.meas_volt = 15
            print 'Set voltage measurement to 15'
        self.ave_time_val = int(self.ave_time_entry.get())
        self.dcbias_val = float(self.dcbias_val_entry.get())
        self.amp_val = float(self.amp_entry.get())
        self.purpose_val = str(self.purpose_entry.get())
        presets = {'title': self.title,
                   'id': self.capchipID,
                   'sample': self.capID,
                   'freqs': self.frequencies,
                   'v': self.meas_volt,
                   'ave': self.ave_time_val,
                   'dc': self.dcbias,
                   'dcv': self.dcbias_val,
                   'amp': self.amp_val,
                   'purp': self.purpose_val}

        with open(os.path.join(self.base_path, 'presets.yml'), 'w') as f:
            yaml.dump(presets, f, default_flow_style=False)

        print 'Chip ID: ' + self.capchipID
        print 'Sample: ' + self.capID
        print 'Frequencies to measure: ' + str(self.frequencies) + 'Hz'
        print 'Voltage of measurement: ' + str(self.meas_volt) + 'V'
        print 'DC bias setting: ' + str(self.dcbias)
        print 'DC bias set to: ' + str(self.dcbias_val) + 'V'
        print 'Amplifier is: ' + str(self.amp_val) + 'x'
        print self.purpose_val

        self.cleanUp()
        
        if self.title:
            self.filename = '%s_%s_%s' % (self.title.replace(' ', '-').replace('_', '-'), self.capID.split(' ')[0], str(time.time()).replace('.', '_'))
        else:
            self.filename = '%s_%s' % (self.capID.split(' ')[0], str(time.time()).replace('.', '_'))
        
        #comment
        self.comment = 'Chip ID: %s... Sample: %s... %s' % (self.capchipID, self.capID, self.purpose_val)

        if not os.path.exists(self.path):
            os.makedirs(self.path)
        data = cap.data_file(self.path, self.filename, self.comment)
        data.dcbias(self.dcbias)
        data.bridge.set_voltage(self.meas_volt)
        data.bridge.set_ave(self.ave_time_val)
        #try:
        if self.dcbias_val:
            if abs(self.dcbias_val) > 15:
                step = 10 * np.sign(self.dcbias_val)
                for volt in np.arange(step, self.dcbias_val+step, step):
                    print 'setting dc voltage to %d' % volt
                    data.lj.set_dc_voltage2(volt, amp=self.amp_val)
                    time.sleep(2)
            else:
                print 'setting dc voltage to %d' % self.dcbias_val
                data.lj.set_dc_voltage(self.dcbias_val, amp=self.amp_val)
        #except:
        #    pass
        while True:
            for ii in xrange(10):
                data.sweep_freq(self.frequencies, 1)

    def cleanUp(self):
        self.destroy()

    def signal_handler(self, signal, frame):
        """After pressing ctrl-C to quit, this function will first run"""
        ds.sort_by_separate_frequencies(self.path, self.filename, self.comment)
        sort_comments.sort_comments()
        print 'quitting'
        sys.exit(0)

def start():
    Setup_Window.mainloop()


if __name__ == '__main__':
    Setup_Window().mainloop()