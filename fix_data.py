import numpy as np
import plot_live as pl
import Tkinter
import tkMessageBox
import os
import sys
sys.path.append('../GPIB')
import get
import yaml
import datetime
import data_files
import itertools
import csv

class Setup_Window(Tkinter.Tk):

    FONT_SIZE = 10
    FONT = 'Arial'

    titles = ['time_', 'tA_', 'tB_', 'c_', 'c_err_', 'loss_', 'loss_err_', 'imC_',
              'imC_err_', 'v_', 'f_']   
    date_override = '10-16-17'
    
    cap_low_cut_def = '1.1'
    cap_high_cut_def = '1.9'

    loss_low_cut_def = '0.'
    loss_high_cut_def = '0.006'    
    
    cap_err_def = '5e-5'
    loss_err_def = '1e-6'
    
    title_def = 'OriginPro'

    def __init__(self):
        """Initialize"""

        """establish the day data is getting taken"""
        date = str(datetime.date.today()).split('-')
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]

        """replace date with date_override"""
        if Setup_Window.date_override:
            datemsg = Setup_Window.date_override.split('-')
            print datemsg
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
        print self.path

        """get list of files in this directory"""
        filenames = data_files.file_name(self.month, self.day, self.year)
        self.filenames = []
        for f in filenames[0]:
            self.filenames.append(f)
        print 'All the files in the directory: ' + str(self.filenames)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('Data Fixer (for importing to Origin Pro)')

        r = 0
        
        Tkinter.Label(self, text='This will genereate a new data file that will be more compatible with data analysis in Origin Pro',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, columnspan=3, stick=Tkinter.W)        
        
        r += 1
        
        Tkinter.Label(self, text='Data File Title:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, stick=Tkinter.W)
        
        self.title_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))        
        self.title_entry.grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.title_entry.insert(0, '%s-%s-%s-%s' % (Setup_Window.title_def, self.month, self.day, self.year))
        
        r += 1
        
        Tkinter.Label(self, text='Capacitance cut off range [pF]:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, stick=Tkinter.W)
        
        self.cap_range_entry_low = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_range_entry_low.grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_low.insert(0, Setup_Window.cap_low_cut_def)
        self.cap_range_entry_high = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_range_entry_high.grid(row=r, column=3, sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_high.insert(0, Setup_Window.cap_high_cut_def)
        
        r += 1
        
        Tkinter.Label(self, text='Loss tangent cut off range:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, stick=Tkinter.W)

        self.loss_range_entry_low = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.loss_range_entry_low.grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_low.insert(0, Setup_Window.loss_low_cut_def)
        self.loss_range_entry_high = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.loss_range_entry_high.grid(row=r, column=3, sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_high.insert(0, Setup_Window.loss_high_cut_def)
        
        r += 1
        
        Tkinter.Label(self, text='Capacitance error [pF]:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, stick=Tkinter.W)
        
        self.cap_error_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_error_entry.grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.cap_error_entry.insert(0, Setup_Window.cap_err_def)
        
        r += 1
        
        Tkinter.Label(self, text='Loss error:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, stick=Tkinter.W)
        
        self.cap_error_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_error_entry.grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.cap_error_entry.insert(0, Setup_Window.loss_err_def)
        
        r += 1

        Tkinter.Label(self, text='Select the files you would like to use:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, sticky=Tkinter.W)
        
        r += 1

        """place checkbox list"""
        self.var_list = [0] * len(self.filenames)
        check_list = [0] * len(self.filenames)
        for ii, f in enumerate(self.filenames):
            comment = self.get_comment(f)       # grab comment from the file
            flength = self.count_rows(f)        # determine number of rows in file
            
            self.var_list[ii] = Tkinter.IntVar()
            Tkinter.Checkbutton(self, text='',
                                variable=self.var_list[ii]).grid(row=r, column=0, sticky=Tkinter.E + Tkinter.W)
            self.var_list[ii].set(1)
            Tkinter.Label(self, text=f,          
                          font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1, sticky=Tkinter.W)

            Tkinter.Label(self, text='%d rows' % flength,          
                          font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=2, sticky=Tkinter.W)
            Tkinter.Label(self, text=comment,
                          font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=3, columnspan=3, sticky=Tkinter.W)
            r += 1

        """Create and place buttons"""
        Tkinter.Button(self, text="Go",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.go).grid(row=r, column=3, sticky=Tkinter.E + Tkinter.W)
        
        r += 1

        Tkinter.Label(self, text="2017 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, columnspan=2,
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

        print "These files were selected: " + str(self.files_to_use)
        self.cap_range = [float(self.cap_range_entry_low.get()), float(self.cap_range_entry_high.get())]
        self.loss_range = [float(self.loss_range_entry_low.get()), float(self.loss_range_entry_high.get())]
        self.title = self.title_entry.get()

        print self.title
        print self.cap_range
        print self.loss_range
        data = self.load_data(self.path, self.files_to_use)
        self.cleanUp()
        
        
        
    
    def get_comment(self, f):
        """Retrieve data file's comment"""
        with open(os.path.join(self.path, f), 'r') as ff:
            comment_list = next(itertools.islice(csv.reader(ff), 1, None))[0].strip('# ').split('... ')
        comment = comment_list[0]
        for c in comment_list[-1:]:
            comment += '; %s' % c
        return comment    
        
    def cleanUp(self):
        """Close window"""
        self.destroy()

    def count_rows(self, f):
        """Return the number of rows in a file"""
        return sum(1 for line in open(os.path.join(self.path, f), 'r'))
    
    def load_data(path, files_to_use):
        skip = 0
        #print skip
        temp_skip = -1
        #print temp_skip
        while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
            temp_skip = skip
            #print 'trying'            
            try:
                data = np.loadtxt(os.path.join(path,
                                               files_to_use[0]),
                                  comments='#', delimiter=',', skiprows=4)
            except StopIteration:
                skip += 1
                #print 'failed'
        if len(files_to_use) > 1:
            for ii, f in enumerate(files_to_use[1:]):
                try:
                    data_temp = np.loadtxt(os.path.join(path, f),
                                           comments='#', delimiter=',',
                                           skiprows=4)
                    try:
                        data = np.append(data, data_temp, axis=0)
                    except ValueError:
                        data = np.append(data, np.array([data_temp]), axis=0)
                except StopIteration:
                    pass
        return data
                
                
if __name__ == '__main__':
    Setup_Window().mainloop()