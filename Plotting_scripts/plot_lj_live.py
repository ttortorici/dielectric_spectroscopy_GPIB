"""
Created on Wed Jul 19 16:52:03 2017

@author: Teddy
"""
# date you want to plot (None will choose today)
date = None

# string of bools to select files
fb = [0,0,0,0,1,1]


import os
import sys
sys.path.append('../GPIB')
import get
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
import datetime
import DateAxisItem
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
    
    
def updateViews():
    global p1a, p1
    p1a.setGeometry(p1.getViewBox().sceneBoundingRect())
    p1a.linkedViewChanged(p1.getViewBox(), p1a.XAxis)
    
    
def update():
    global path, files, c_curves, l_curves, lt_curves, ct_curves, ljt_curves
    data = load_data(path, files)
    columns = np.shape(data)[1]
    if columns == 21:
        o = 0
    elif columns == 24:
        o = 1
    elif columns == 33:
        o = 4
    elif columns == 36:
        o = 4
    #print o
    ts = [data[:, 0], data[:, 7+o], data[:, 14+o+o]]
    Ts = [data[:, 1], data[:, 8+o], data[:, 15+o+o]]
    Cs = [data[:, 3], data[:, 10+o], data[:, 17+o+o]]
    Ls = [data[:, 4], data[:, 11+o], data[:, 18+o+o]]
    V1s = [data[:, 6], data[:, 13+o], data[:, 20+o+o]]
    V2s = [data[:, 8], data[:, 15+o], data[:, 22+o+o]]
    for curve, t, C in zip(ct_curves, ts, Cs):
        curve.setData(x=t, y=C)
    for curve, t, L in zip(lt_curves, ts, Ls):
        curve.setData(x=t, y=L)
    for curve, V, C in zip(c_curves, V2s, Cs):
        curve.setData(x=V, y=C)
    for curve, V, L in zip(l_curves, V2s, Ls):
        curve.setData(x=V, y=L)
    data = np.column_stack((np.concatenate(ts),
                            np.concatenate(Ts),
                            np.concatenate(V1s),
                            np.concatenate(V2s)))
    data = np.array(sorted(data, key=lambda row: row[0]))
    for ii, curve in enumerate(ljt_curves):
        curve.setData(x=data[:, 0], y=data[:, ii+2])
    data = np.array(sorted(data, key=lambda row: row[1]))
    
    

path, base_path, date = get_path(date)
files = get_files(date, file_bool=fb)

title = "Live Plotting %s/%s/%s" % date
app = pg.QtGui.QApplication([])
win = pg.GraphicsWindow(title="Live Plotting")
win.resize(1900, 1000)
win.setWindowTitle(title)
    
# enable antialiasing
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title=title,
                 axisItems={'bottom':DateAxisItem.DateAxisItem('bottom')},
                 row=0, col=0)
p1.setLabel('left', 'Capacitance (pF)')
p1.showAxis('right')
p1.setLabel('right', 'Loss Tangent')

p1a = pg.ViewBox()
p1.scene().addItem(p1a)
p1.getAxis('right').linkToView(p1a)
p1a.setXLink(p1)
p1.setXLink(p1a)
p1 = win.addPlot(title=title, row=0, col=0)
p1.addLegend()

p2 = win.addPlot(title='',
                 axisItems={'bottom':DateAxisItem.DateAxisItem('bottom')},
                 row=1, col=0)
p2.setLabel('left', 'LabJack (V)')
p2.addLegend()

p2.setXLink(p1)

#p2.setXLink(p1)

p3 = win.addPlot(title='', row=0, col=1)
p3.setLabel('left', 'Capacitance (pF))')
p3.setLabel('bottom', 'LabJack CH2 (V)')
p3.addLegend()

p4 = win.addPlot(title='', row=1, col=1)
p4.setLabel('left', 'Loss Tangent')
p4.setLabel('bottom', 'LabJack CH2 (V)')

p3.setXLink(p4)
                
#p3.setLabel('bottom', 'Temperature (K)')
#p4.addLegend()

#p.showAxis('right')
#p.setLabel('right', 'Loss Tangent')
c_curves = [''] * 3
l_curves = [''] * 3
ct_curves = [''] * 6
lt_curves = [''] * 3
labels = ['10kHz', '1kHz', '100Hz']
for ii, label in enumerate(labels):
    c_curves[ii] = p3.plot(pen=(ii, 6), name=label)
    l_curves[ii] = p4.plot(pen=(ii+3, 6), name=label)
    ct_curves[ii] = p1.plot(pen=(ii, 6), name=label+' capacitance')
    ct_curves[ii+3] = p1.plot(pen=(ii+3, 6), name=label+' loss')
    lt_curves[ii] = pg.PlotCurveItem(pen=(ii+3, 6), name=label)
    p1a.addItem(lt_curves[ii])
    
ljt_curves = [''] * 2
labels = ['LJ CH1', 'LJ CH2']
for ii, label in enumerate(labels):
    ljt_curves[ii] = p2.plot(pen=(ii, 2), name=label)
    
updateViews()
p1.getViewBox().sigResized.connect(updateViews)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)
pg.QtGui.QApplication.instance().exec_()       
    
    
                  
        

    