# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:52:03 2017

@author: Teddy
"""

import os
import sys
sys.path.append('../GPIB')
import get
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
import datetime
import time
import data_files

pg.setConfigOption('background','w')
pg.setConfigOption('foreground','k')

def get_path(date=None):
    """set date"""
    current_date = str(datetime.date.today()).split('-')
    year = current_date[0]
    month = current_date[1]
    day = current_date[2]
    if date:
        if '-' in date:
            datemsg = date.split('-')
        elif '/' in date:
            datemsg = date.split('/')
        else:
            try:
                int(date)
            except ValueError:
                raise ValueError('Invalid input for date: try mm-dd-yyyy')
            datemsg = [date]
        if len(datemsg) == 2:
            month = datemsg[0]
            day = datemsg[1]
        elif len(datemsg) == 3:
            year = datemsg[2]
            month = datemsg[0]
            day = datemsg[1]
        elif len(datemsg) == 1:
            try:
                day_temp = int(datemsg[0])
                if day_temp > int(day):
                    month = str(int(month) - 1)
                    if int(month) == 0:
                        month = '12'
                day = datemsg[0]
            except ValueError:
                pass
    # make sure the numbers come out right
    if len(day) == 1:
        day = '0' + day
    if len(month) == 1:
        month = '0' + month
    if len(year) == 2:
        year = '20' + year
        
    base_path = os.path.join(get.googledrive(), 'Dielectric_data',
                             'Teddy')
    path = os.path.join(base_path, year, month, day)
    
    return path, base_path, (month, day, year)


def get_files(date, file_bool=None):
    """get list of files in this directory"""
    month = date[0]
    day = date[1]
    year = date[2]
    filenames_all = data_files.file_name_sorted(month, day, year)
    filenames = []
    for f in filenames_all[0]:
        if '_sorted' in f.lower():
            filenames.append(f)
    print 'All the files in the directory: ' + str(filenames)
        
    """use file_bool to select files"""
    if file_bool:
        if len(filenames) < len(file_bool):
            file_bool = file_bool[:len(filenames)]
        files_to_use = []
        for ii, b in enumerate(file_bool):
            if b:
                files_to_use.append(filenames[ii])
    else:
        files_to_use = filenames
    return files_to_use
    
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
            #print 'passed'
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
    #print np.shape(data)
    """columns = np.shape(data)[1]
    if columns == 21:
        o = 0
    elif columns == 24:
        o = 1
    elif columns == 36:
        o = 4"""
    return data
    
def update():
    global path, files, c_curves, p
    data = load_data(path, files)
    columns = np.shape(data)[1]
    if columns == 21:
        o = 0
    elif columns == 24:
        o = 1
    elif columns == 36:
        o = 4
    #print o
    Ts = [data[:, 0], data[:, 7+o], data[:, 14+o+o]]
    Cs = [data[:, 3], data[:, 10+o], data[:, 17+o+o]]
   
    for curve, T, C in zip(c_curves, Ts, Cs):
        curve.setData(x=T, y=C)
    
    
fb = [1,1,0]

path, base_path, date = get_path()
files = get_files(date, file_bool=fb)

title = "Live Plotting %s/%s/%s" % date
app = pg.QtGui.QApplication([])
win = pg.GraphicsWindow(title="Live Plotting")
win.resize(1000, 600)
win.setWindowTitle(title)
    
# enable antialiasing
pg.setConfigOptions(antialias=True)

p = win.addPlot(title=title)
p.setLabel('left', 'Capacitance (pF)')
p.setLabel('bottom', 'Temperature (K)')
p.addLegend()
#p.showAxis('right')
#p.setLabel('right', 'Loss Tangent')
c_curves = [''] * 3
labels = ['10kHz', '1kHz', '100Hz']
for ii, label in enumerate(labels):
    curve = p.plot(pen=(ii, 3), name=label)
    c_curves[ii] = curve

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)
pg.QtGui.QApplication.instance().exec_()       
    
    
                  
        

    