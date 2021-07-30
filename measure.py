"""
Dielectric spectroscopy data taking tool written by Teddy.

When you run "python measure.py" in cmd, you can add the following parametrs:

python measure.py 'preset-xxx.py'
    - where 'preset-xxx.py' can be accessed be sys.argv[1] and will override taking most recent

Original written in 2017
Update 2021:
-more sophisticated GUI control with more specific options
-updated yaml to go into another folder so that they don't get written over and the history can be seen
-new features for being able to automate post-processing
"""

import sys
import numpy as np
import glob
import os
import time
import datetime
import yaml
try:
    import Tkinter
except ImportError:
    import tkinter as Tkinter
import client_tools as tools
import data_files
import get
import csv
import calculations as calc


class SetupWindow(Tkinter.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    LJ_CHs = 4

    def __init__(self):
        print('\n\n\n')
        """establish the day data is getting taken
        self.date has attributes .year, .month, .day, .hour, .min, .second, .microsecond"""
        self.date = datetime.datetime.fromtimestamp(time.time())

        # get filepath in googledrive
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy-2')

        self.lj_chs = []                    # will be used later
        self.path = self.base_path          # will be added on to later

        # load presets
        yaml_fname = ''
        if len(sys.argv) > 1:
            yaml_fname = str(sys.argv[1]).lower()
        if 'preset' not in yaml_fname:
            yaml_fname = max(glob.glob(os.path.join(self.base_path, 'presets') + '\*yml'), key=os.path.getctime)
        yaml_f = os.path.join(self.base_path, 'presets', yaml_fname)
        with open(yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('Measure Capacitance')

        """
        create and place labels
        """
        columns = 5

        r = 0

        """TITLE LINE"""
        Tkinter.Label(self, text='Please enter parameters then press "START EXPERIMENT" to start the measurement',
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)

        r += 1

        """PORT FOR SERVER COMM"""
        Tkinter.Label(self, text="Port to communicate with GPIB server:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.port = preset['port']
        self.port_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.port_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.port_entry.insert(0, self.port)

        r += 1

        """INSTRUMENT"""
        Tkinter.Label(self, text="Instrument used:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.inst = preset['inst']
        self.inst_selection = Tkinter.IntVar(self)

        inst_setting = {'ah': 0,
                        'hp': 1,
                        'other': 2}

        self.inst_selection.set(inst_setting[self.inst])

        Tkinter.Radiobutton(self, text="Andeen-Hagerling", variable=self.inst_selection, value=0,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.instselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="Hewlett Packard", variable=self.inst_selection, value=1,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.instselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="Other", variable=self.inst_selection, value=2,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.instselect).grid(row=r, column=3)
        self.instselect()       # prints current selection

        r += 1

        """CRYOSTAT"""
        Tkinter.Label(self, text="Cryostat used:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.cryo = preset['cryo']
        self.cryo_selection = Tkinter.IntVar(self)

        cryo_setting = {'Desert-LN': 0,
                        'Desert-He': 1,
                        '40K': 2,
                        '4K': 3}
        self.cryo_selection.set(cryo_setting[self.cryo])

        Tkinter.Radiobutton(self, text="DesertCryo LN", variable=self.cryo_selection, value=0,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="DesertCryo He", variable=self.cryo_selection, value=1,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="40 K Cryo", variable=self.cryo_selection, value=2,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=3)
        Tkinter.Radiobutton(self, text="4 K Cryo", variable=self.cryo_selection, value=3,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.cryoselect).grid(row=r, column=4)
        self.cryoselect()  # prints current result

        r += 1

        """PURPOSE"""
        Tkinter.Label(self, text="Purpose of measurement:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.purp = preset['purp']
        self.purp_selection = Tkinter.IntVar(self)

        purp_setting = {'cal': 0,
                        'powder': 1,
                        'film': 2,
                        'other': 3}
        self.purp_selection.set(purp_setting[self.purp])

        Tkinter.Radiobutton(self, text="Calibration", variable=self.purp_selection, value=0,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.purpselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="Powder", variable=self.purp_selection, value=1,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.purpselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="Film", variable=self.purp_selection, value=2,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.purpselect).grid(row=r, column=3)
        Tkinter.Radiobutton(self, text="Other", variable=self.purp_selection, value=3,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.purpselect).grid(row=r, column=4)
        self.purpselect()  # prints current result

        r += 1

        """CAPACITOR CHIP ID"""
        Tkinter.Label(self, text="Capacitor Chip ID:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.capchipID = preset['id']
        self.capchipID_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.capchipID_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.capchipID_entry.insert(0, self.capchipID)

        r += 1

        """SAMPLE NAME"""
        Tkinter.Label(self, text="Sample (if calibrating, what's the substrate?):",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.sample = preset['sample']
        self.sample_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.sample_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.sample_entry.insert(0, self.sample)

        r += 1

        """FREQUENCIES TO MEASURE"""
        Tkinter.Label(self, text="Frequencies of measurement [in Hz, separate by commas]:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.frequencies = preset['freqs']
        self.freq_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.freq_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.freq_entry.insert(0, str(self.frequencies).strip('[').strip(']'))

        r += 1

        """CALIBRATION LOCATION"""
        Tkinter.Label(self,
                      text="Calibration file location (use / not \\) [Google "
                           "Drive/Dielectric_data/Teddy-2/1-Calibrations/...]:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.cal = preset['cal']
        self.cal_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.cal_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.cal_entry.insert(0, str(self.cal).strip('[').strip(']'))

        r += 1

        """FILM THICKNESS"""
        Tkinter.Label(self,
                      text="Film Thickness (only used if measuring a film) [um]:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.filmT = preset['filmT']
        self.filmT_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.filmT_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.filmT_entry.insert(0, str(self.filmT).strip('[').strip(']'))

        r += 1

        """MEASURE VOLTAGE"""
        Tkinter.Label(self, text="Measurement Voltage amplitude [in Volts RMS for AH.. in Volts for HP]:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.meas_volt = preset['v']
        self.volt_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.volt_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.volt_entry.insert(0, self.meas_volt)

        r += 1

        """AVERAGING"""
        Tkinter.Label(self, text="Averaging setting [0-15 for AH.. any positive integer for HP]:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.ave_time_val = preset['ave']
        self.ave_time_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.ave_time_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.ave_time_entry.insert(0, self.ave_time_val)

        r += 1

        """DC BIAS SETTING"""
        Tkinter.Label(self, text="DC Bias Setting (AH only):",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.dcbias = preset['dc']
        self.dcbias_selection = Tkinter.IntVar(self)

        dc_setting = {'off': 0,
                      'low': 1,
                      'high': 2}
        self.dcbias_selection.set(dc_setting[self.dcbias])

        Tkinter.Radiobutton(self, text="Off", variable=self.dcbias_selection, value=0,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.dcselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="I-Low", variable=self.dcbias_selection, value=1,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.dcselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="I-High", variable=self.dcbias_selection, value=2,
                            font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                            command=self.dcselect).grid(row=r, column=3)
        self.dcselect()  # prints current result

        r += 1

        """DESIRED DC VALUE"""
        Tkinter.Label(self, text="DC Bias Value [0-100V] (AH only):",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.dcbias_val = preset['dcv']
        self.dcbias_val_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.dcbias_val_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.dcbias_val_entry.insert(0, self.dcbias_val)

        r += 1

        """DC AMPLIFIER VALUE"""
        Tkinter.Label(self, text="Amplification level on DC bias (AH only):",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.amp_val = preset['amp']
        self.amp_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.amp_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.amp_entry.insert(0, self.amp_val)

        r += 1

        """LABJACK CHANNEL LABELS"""
        if len(preset['lj']) == SetupWindow.LJ_CHs:
            self.lj_val = preset['lj']
        else:
            self.lj_val = [''] * SetupWindow.LJ_CHs
        self.lj_entry = [0] * SetupWindow.LJ_CHs

        for ii, lj_v in enumerate(self.lj_val):
            Tkinter.Label(self, text="Labjack CH%d Label (optional):" % ii,
                          font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
            self.lj_entry[ii] = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
            self.lj_entry[ii].grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
            self.lj_entry[ii].insert(0, lj_v)
            r += 1

        """COMMENT"""
        Tkinter.Label(self, text="Comments:",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.comment_val = preset['comment']
        self.comment_entry = Tkinter.Entry(self, font=(SetupWindow.FONT, SetupWindow.FONT_SIZE))
        self.comment_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        self.comment_entry.insert(0, self.comment_val)

        r += 1

        """GO BUTTON"""
        Tkinter.Button(self, text="START EXPERIMENT",
                       font=(SetupWindow.FONT, SetupWindow.FONT_SIZE),
                       command=self.go).grid(row=r, column=1, columnspan=columns - 1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        Tkinter.Label(self, text="2021 Teddy Tortorici",
                      font=(SetupWindow.FONT, SetupWindow.FONT_SIZE)).grid(row=r, column=0, columnspan=2,
                                                                           sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.killWindow)

        self.attributes('-topmost', True)

    """
    DEFINITIONS FOR SELECTION TOOL IN GUI
    """

    def instselect(self):
        if self.inst_selection.get() == 0:
            self.inst = 'ah'
            print('Andeen-Hagerling 2700A Bridge will be used')
        elif self.inst_selection.get() == 1:
            self.inst = 'hp'
            print('Hewlett Packard 4275A Bridge will be used')
        elif self.inst_selection.get() == 2:
            self.inst = 'other'
            print('A different instrument will be used')

    def cryoselect(self):
        if self.cryo_selection.get() == 0:
            self.cryo = 'Desert-LN'
            print('DesertCryo being used with liquid nitrogen')
        elif self.cryo_selection.get() == 1:
            self.cryo = 'Desert-He'
            print('DesertCryo being used with liquid helium')
        elif self.cryo_selection.get() == 2:
            self.cryo = '40K'
            print('Closed cycle 40K cryo being used')
        elif self.cryo_selection.get() == 3:
            self.cryo = '4K'
            print('Closed cycle 4K cryo being used')

    def purpselect(self):
        if self.purp_selection.get() == 0:
            self.purp = 'cal'
            print('Will measure a calibration set on a bare capacitor')
        elif self.purp_selection.get() == 1:
            self.purp = 'powder'
            print('Will measure dielectric spectroscopy with a powder sample')
        elif self.purp_selection.get() == 2:
            self.purp = 'film'
            print('Will measure dielectric spectroscopy with a film sample')
        elif self.purp_selection.get() == 3:
            self.purp = 'other'
            print('Will perform another type of measurement')

    def dcselect(self):
        if self.dcbias_selection.get() == 0:
            self.dcbias = 'off'
            print('DC bias turned off')
        elif self.dcbias_selection.get() == 1:
            self.dcbias = 'low'
            print('DC bias turned to low')
        elif self.dcbias_selection.get() == 2:
            self.dcbias = 'high'
            print('DC bias turned to high')

    """
    MAIN DEFINITION
    """

    def go(self):
        self.port = int(self.port_entry.get())
        self.capchipID = str(self.capchipID_entry.get())
        self.sample = str(self.sample_entry.get())
        unsorted_f = [float(freq) for freq in str(self.freq_entry.get()).split(',')]
        self.frequencies = sorted(unsorted_f)[::-1]
        if len(self.frequencies) == 0:
            raise IOError('Invalid frequency input')
        self.cal = str(self.cal_entry.get())
        self.filmT = abs(float(self.filmT_entry.get()))
        self.meas_volt = abs(float(self.volt_entry.get()))
        if self.meas_volt > 15:
            self.meas_volt = 15
            print('Set voltage measurement to 15')
        self.ave_time_val = int(self.ave_time_entry.get())
        self.dcbias_val = float(self.dcbias_val_entry.get())
        self.amp_val = float(self.amp_entry.get())
        for ii, lj_e in enumerate(self.lj_entry):
            self.lj_val[ii] = str(lj_e.get())
        self.comment_val = str(self.comment_entry.get())
        presets = {'port': self.port,
                   'inst': self.inst,
                   'cryo': self.cryo,
                   'purp': self.purp,
                   'id': self.capchipID,
                   'sample': self.sample,
                   'freqs': self.frequencies,
                   'cal': self.cal,
                   'filmT': self.filmT,
                   'v': self.meas_volt,
                   'ave': self.ave_time_val,
                   'dc': self.dcbias,
                   'dcv': self.dcbias_val,
                   'amp': self.amp_val,
                   'lj': self.lj_val,
                   'comment': self.comment_val}

        self.cal = os.path.join(self.base_path, 'Calibration', self.cal)

        save_name = f'presets{self.date.year:04}-{self.date.month:02}-{self.date.day:02}_{self.date.hour:02}.yml'
        save_presets = os.path.join(self.base_path, 'presets', save_name)
        with open(save_presets, 'w') as f:
            yaml.dump(presets, f, default_flow_style=False)

        self.killWindow()

        """Populate list with labels for LabJack channel"""
        for ii, lj_ in enumerate(self.lj_val):
            if not lj_ == '':
                self.lj_chs.append(ii)

        """Path to write file"""
        if self.purp == 'cal':
            self.path = os.path.join(self.path, '1-Calibrations', f'{self.date.year:04}')
            self.filename = f'calibrate_{self.capchipID}_{self.inst}_{self.cryo}_{self.month}-'
        elif self.purp == 'powder':
            self.path = os.path.join(self.path, '2-Powders')
        elif self.purp == 'film':
            self.path = os.path.join(self.path, '3-Films')
        elif self.purp == 'other':
            self.path = os.path.join(self.path, 'Other')
        if not self.purp == 'cal':
            self.path = os.path.join(self.path, f'{self.date.year:04}-{self.date.month:02}')
            self.filename = f'{self.sample}_{self.capchipID}_{self.purp}_{self.inst}_{self.cryo}_'
        self.filename += f'{self.date.day:02}_{self.date.hour:02}-{self.date.minute:02}'

        print(self.filename)

        """FILE HEADER COMMENT"""
        comment_line = 'Chip ID:, {}.., Sample:, {}.., DCB Setting:, {}.., {}'.format(self.capchipID,
                                                                                      self.sample,
                                                                                      self.dcbias,
                                                                                      self.comment_val)
        for ii, ch in enumerate(self.lj_chs):
            comment_line += '.., LJ ch{}:, {}'.format(ch, self.lj_val[ch])
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if int(self.dcbias_val):
            lj_chs = 'dc'
        else:
            lj_chs = self.lj_chs

        if self.purp == 'film' and self.cal and isinstance(self.cal, str):
            fitC, fitD = load_calibration(self.cal)

            bareC_RT = 0
            if self.inst == 'ah':
                fit_index = 0
            elif self.inst == 'hp':
                fit_index = 1
            freq_bareC = self.frequencies[fit_index]
            temp_bareC = 297                            # Kelvin
            for ii, a in enumerate(fitC[fit_index]):
                bareC_RT += a * temp_bareC ** ii
            gapW = calc.find_gap(bareC_RT)

            comment_line += ', Film Thickness {} um, '.format(self.filmT)
            comment_line += 'Bare Capacitance of {} pF at {} K and {} Hz'.format(bareC_RT, temp_bareC, freq_bareC)
            comment_line += ' was used to produce the gapW size of {} um'.format(gapW)

            data = data_files.DielectricConstant(self.path, self.filename, self.port, self.frequencies, self.filmT,
                                            gapW, fitC, fitD,
                                            self.inst, self.cryo, comment_line, lj_chs)
        else:
            data = data_files.DataFile(self.path, self.filename, self.port,
                                  self.frequencies, self.inst, self.cryo,
                                  comment_line, lj_chs)

        print('created datafile')
        data.bridge.dcbias(self.dcbias)
        data.bridge.set_voltage(self.meas_volt)
        data.bridge.set_ave(self.ave_time_val)

        if self.dcbias_val:
            if abs(self.dcbias_val) > 15:
                step = 10 * np.sign(self.dcbias_val)
                for volt in np.arange(step, self.dcbias_val + step, step):
                    print('setting dc voltage to %d' % volt)
                    data.lj.set_dc_voltage2(volt, amp=self.amp_val)
                    time.sleep(2)
            else:
                print('setting dc voltage to %d' % self.dcbias_val)
                data.lj.set_dc_voltage2(self.dcbias_val, amp=self.amp_val)

        while True:
            print('measuring capacitance')
            for ii in range(10):
                data.sweep_freq()

    def killWindow(self):
        self.destroy()


def start():
    SetupWindow().mainloop()


def load_calibration(path):
    cal_data = np.loadtxt(os.path.join(path), comments='#', delimiter=',', skiprows=3)
    with open(path) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if len(row) > 1:        # this will grab the first line with the labels
                labels = row
                break
    Tind = []       # indexes for temperatures
    Cind = []       # indexes for capacitance
    Dind = []       # indexes for loss tangent

    for ii, label in enumerate(labels):
        if 'temperature' in label.lower() and 'B' not in label:
            Tind.append(ii)
        elif 'capacitance' in label.lower():
            Cind.append(ii)
        elif 'loss tangent' in label.lower():
            Dind.append(ii)

    Cfit = [0] * len(Tind)
    Dfit = [0] * len(Tind)
    for ii in range(Cfit):
        Cfit[ii] = np.polyfit(cal_data[:, Tind[ii]], cal_data[:, Cind[ii]], 2)
        Dfit[ii] = np.polyfit(cal_data[:, Tind[ii]], cal_data[:, Dind[ii]], 1)

    return Cfit, Dfit


if __name__ == '__main__':
    SetupWindow().mainloop()
