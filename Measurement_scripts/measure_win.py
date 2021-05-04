import threading
import Tkinter
import tkMessageBox
import capacitance_measurement_tools as cap
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
    LJ_CHs = 4

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
        
        Tkinter.Label(self, text="Bare Capacitance (optional) [in pF, separate by commas corresponding to above frequencies]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Bare loss tangent (optional) [in pF, separate by commas corresponding to above frequencies]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Measurement Voltage amplitude [in Volts RMS for AH.. in Volts for HP]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Averaging setting [0-15 for AH.. any positive integer for HP]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="DC Bias Setting (AH only):",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="DC Bias Value [0-100V] (AH only):",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        Tkinter.Label(self, text="Amplification level on DC bias (AH only):",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        r += 1
        
        for ii in xrange(Setup_Window.LJ_CHs):
            Tkinter.Label(self, text="Labjack CH%d Label (optional):" % ii,
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
        Bare Capacitances
        """
        self.bare_Cs = preset['bare_c']
        self.bare_c_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.bare_c_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.bare_c_entry.insert(0, str(self.bare_Cs).strip('[').strip(']'))
        
        self.bare_Ls = preset['bare_l']
        self.bare_l_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.bare_l_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        r += 1
        self.bare_l_entry.insert(0, str(self.bare_Ls).strip('[').strip(']'))
        

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
        Labjack
        """
        if len(preset['lj']) == Setup_Window.LJ_CHs:
            self.lj_val = preset['lj']            
        else:
            self.lj_val = [''] * Setup_Window.LJ_CHs            
        self.lj_entry = [0] * Setup_Window.LJ_CHs
        for ii, lj_v in enumerate(self.lj_val):
            self.lj_entry[ii] = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
            self.lj_entry[ii].grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
            self.lj_entry[ii].insert(0, lj_v)
            r += 1

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
        self.title = str(self.title_entry.get())
        self.capchipID = str(self.capchipID_entry.get())
        self.capID = str(self.capID_entry.get())
        unsorted_f = [float(freq) for freq in str(self.freq_entry.get()).split(',')]
        self.frequencies = sorted(unsorted_f)[::-1]
        if len(self.frequencies) == 0:
            raise IOError('Invalid frequency input')
        if not self.bare_c_entry.get() == '':
            unsorted_c = [float(c) for c in str(self.bare_c_entry.get()).split(',')]
            self.bare_Cs = [c for _, c in sorted(zip(unsorted_f, unsorted_c))[::-1]]
        else:
            self.bare_Cs = ''
        if not self.bare_l_entry.get() == '':
            unsorted_l = [float(los) for los in str(self.bare_l_entry.get()).split(',')]
            self.bare_Ls = [los for _, los in sorted(zip(unsorted_f, unsorted_l))[::-1]]
        else:
            self.bare_Ls = ''
        self.meas_volt = abs(float(self.volt_entry.get()))
        if self.meas_volt > 15:
            self.meas_volt = 15
            print 'Set voltage measurement to 15'
        self.ave_time_val = int(self.ave_time_entry.get())
        self.dcbias_val = float(self.dcbias_val_entry.get())
        self.amp_val = float(self.amp_entry.get())
        for ii, lj_e in enumerate(self.lj_entry):
            self.lj_val[ii] = str(lj_e.get())
        self.purpose_val = str(self.purpose_entry.get())
        presets = {'title': self.title,
                   'id': self.capchipID,
                   'sample': self.capID,
                   'freqs': self.frequencies,
                   'bare_c': self.bare_Cs,
                   'bare_l': self.bare_Ls,
                   'v': self.meas_volt,
                   'ave': self.ave_time_val,
                   'dc': self.dcbias,
                   'dcv': self.dcbias_val,
                   'amp': self.amp_val,
                   'lj': self.lj_val,
                   'purp': self.purpose_val}
        
        with open(os.path.join(self.base_path, 'presets.yml'), 'w') as f:
            yaml.dump(presets, f, default_flow_style=False)
        
        self.lj_chs = []
        for ii, lj_ in enumerate(self.lj_val):
            if not lj_ == '':
                self.lj_chs.append(ii)

        self.cleanUp()
        
        if self.title:
            self.filename = '%s_%s_%s_%s_sorted' % (self.title.replace(' ', '-').replace('_', '-'), self.capchipID.split(' ')[0], self.capID.split(' ')[0], str(time.time()).replace('.', '_'))
        else:
            self.filename = '%s_%s_%s_sorted' % (self.capchipID.split(' ')[0], self.capID.split(' ')[0], str(time.time()).replace('.', '_'))
        
        #comment
        self.comment = 'Chip ID: %s... Sample: %s... DCB Setting:%s... %s' % (self.capchipID, self.capID, str(self.dcbias), self.purpose_val)
        for ii, ch in enumerate(self.lj_chs):
            self.comment += '... LJ ch%d: %s' % (ch, self.lj_val[ch])
        if not self.bare_Cs == '':
            for c, f in zip(self.bare_Cs, self.frequencies):
                self.comment += '... Bare C at %d Hz [pF]: %0.5f' % (f, c)
        if not self.bare_Ls == '':
            for l, f in zip(self.bare_Ls, self.frequencies):
                self.comment += '... Bare loss at %d Hz: %0.1e' % (f, l)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if int(self.dcbias_val):
            lj_chs = 'dc'
        else:
            lj_chs = self.lj_chs
        data = cap.data_file(self.path, self.filename,
                             unique_freqs=self.frequencies,
                             comment=self.comment, lj_chs=lj_chs)
        print 'created datafile'
        data.dcbias(self.dcbias)
        data.bridge.set_voltage(self.meas_volt)
        data.bridge.set_ave(self.ave_time_val)
        
        print 'Chip ID: ' + self.capchipID
        print 'Sample: ' + self.capID
        print 'Frequencies to measure: ' + str(self.frequencies) + 'Hz'
        if not self.bare_Cs == '':
            print 'Bare Capacitances: ' + str(self.bare_Cs) + 'pF'
        if not self.bare_Ls == '':
            print 'Bare Loss Tangents: ' + str(self.bare_Ls)
        print 'Voltage of measurement: ' + str(self.meas_volt) + 'V'
        print 'DC bias setting: ' + str(self.dcbias)
        print 'DC bias set to: ' + str(self.dcbias_val) + 'V'
        print 'Amplifier is: ' + str(self.amp_val) + 'x'
        print self.purpose_val        
        
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
                data.lj.set_dc_voltage2(self.dcbias_val, amp=self.amp_val)
        #except:
        #    pass
        while True:
        #if True:
            if 'resistance' in self.title.lower():
                print 'measuring resistance'
                for ii in xrange(10):
                    data.sweep_freq_win_RC()
            elif 'impedance' in self.title.lower():
                print 'measuring impedence'
                for ii in xrange(10):
                    data.sweep_freq_win_Z()
            elif 'average' in self.purpose_val.lower():
                print 'averaging'
                ave_loc = self.purpose_val.lower().find('average')+len('average ')
                aves = int(self.purpose_val[ave_loc:ave_loc+2])
                Caps = [0] * aves
                Loss = [0] * aves
            
                '''take data to average over'''
                for ii in xrange(aves):
                    (Caps[ii], Loss[ii]) = data.sweep_freq_win_return()
                    
                '''calculate averages and std devs'''
                print Caps
                cap_ave = sum(Caps)/float(aves)
                cap_std = np.sqrt(sum((Caps-cap_ave)**2)/(float(aves)-1))
                los_ave = sum(Loss)/float(aves)
                los_std = np.sqrt(sum((Loss-los_ave)**2)/(float(aves)-1))
                
                sig_figs_C = [0] * len(data.unique_freqs)
                sig_figs_L = [0] * len(data.unique_freqs)
                
                deltaC = [0] * len(data.unique_freqs)
                deltaL = [0] * len(data.unique_freqs)               
                
                loop_over = zip(xrange(len(data.unique_freqs)), data.unique_freqs, cap_ave, los_ave, cap_std, los_std)
                for ii, f, c_av, l_av, c_sd, l_sd in loop_over:
                    '''find error and sig figs'''
                    sig_figs_C[ii] = int(('%.0e'%c_sd)[len('%.0e'%c_sd)-2:len('%.0e'%c_sd)])
                    if ('%.0e'%c_sd)[0] == 1:
                        sig_figs_C[ii] += 1
                    sig_figs_L[ii] = int(('%.0e'%l_sd)[len('%.0e'%l_sd)-2:len('%.0e'%l_sd)])
                    if ('%.0e'%l_sd)[0] == 1:
                        sig_figs_L[ii] += 1
                            
                    '''Find change from bare'''
                    if not self.bare_Cs == '':
                        deltaC[ii] = c_av-self.bare_Cs[ii]
                    if not self.bare_Ls == '':
                        deltaL[ii] = l_av-self.bare_Ls[ii]
                    
                    '''Establish unit for frequency'''
                    if f < 1000:
                        unit = 'Hz'
                    elif f < 1e6:
                        unit = 'kHz'
                        f /= 1000.
                    elif f < 1e9:
                        unit = 'MHz'
                        f /= 1e6
                    elif f < 1e12:
                        unit = 'GHz'
                        f /= 1e9
                    C_string = ('Capacitance at %d %s is ({0:.%sf} +/- '%(f, unit, str(sig_figs_C[ii]))).format(c_av) + ('{0:.%sf}) pF'%str(sig_figs_C[ii])).format(c_sd)
                    L_string = ('Loss Tangent at %d %s is ({0:.%sf} +/- '%(f, unit, str(sig_figs_L[ii]))).format(l_av) + ('{0:.%sf}) pF'%str(sig_figs_L[ii])).format(l_sd)
                    data.write_row2('# %s' % C_string)
                    data.write_row2('# %s' % L_string)
                    print C_string
                    print L_string
                    
                    if not self.bare_Cs == '':
                        if deltaC[ii] < 0:
                            qualifier = 'decreased'
                        else:
                            qualifier = 'increased'
                        delC_string = ('Capacitance at %d %s %s by {0:.%sf} fF'%(f, unit, qualifier, str(sig_figs_C[ii]-3))).format(abs(deltaC[ii])*1000.)
                        data.write_row2('# %s' % delC_string)
                        print delC_string
                    if not self.bare_Ls == '':
                        if deltaL[ii] < 0:
                            qualifier = 'decreased'
                        else:
                            qualifier = 'increased'
                        delL_string = ('Loss Tangent at %d %s %s by {0:.%sf}'%(f, unit, qualifier, str(sig_figs_L[ii]))).format(abs(deltaL[ii]))
                        data.write_row2('# %s' % delL_string)
                        print delL_string
                    
                '''write data columnized'''
                data.write_row2('# Labels')
                labels = ['time', '', '', 'Cap Average [pf]', 'Loss Average', '', 'Frequency [Hz]']
                labels2 = ['time', '', '', 'Cap Change [pf]', 'Loss Change', '', 'Frequency [Hz]']
                label_row = []
                label2_row = []
                ave_data = [0] * 7 * len(data.unique_freqs)
                #if (not (self.bare_Cs == '')) or (not (self.bare_Ls == '')):
                del_data = [0] * 7 * len(data.unique_freqs)
                for ii, f in enumerate(data.unique_freqs):
                    label_row.extend(labels)
                    label2_row.extend(labels2)
                    ave_data[ii*7] = time.time()
                    ave_data[3+ii*7] = cap_ave[ii]
                    ave_data[4+ii*7] = los_ave[ii]
                    ave_data[6+ii*7] = f
                    if not self.bare_Cs == '':
                        del_data[3+ii*7] = deltaC[ii]
                    if not self.bare_Ls == '':
                        del_data[4+ii*7] = deltaL[ii]
                    if not (self.bare_Cs == '' and self.bare_Ls == ''):
                        del_data[ii*7] = time.time()
                        del_data[6+ii*7] = f
                label_row[0] = '#' + label_row[0]
                label2_row[0] = '#' + label2_row[0]
                data.write_row2(label_row)
                data.write_row2(ave_data)
                if not (self.bare_Cs == '' and self.bare_Ls == ''):
                    data.write_row2(label2_row)
                    data.write_row2(del_data)
                data.bridge.set_freq(10000)
                data.bridge.meas_cont(1)
                break
            else:
                print 'measuring capacitance'
                for ii in xrange(10):
                    data.sweep_freq_win()
                    

    def cleanUp(self):
        self.destroy()

def start():
    Setup_Window.mainloop()


if __name__ == '__main__':
    Setup_Window().mainloop()