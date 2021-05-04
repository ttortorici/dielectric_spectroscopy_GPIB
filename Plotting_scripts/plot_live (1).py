# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:52:03 2017

@author: Teddy
"""
# date you want to plot (None will choose today)
date = None

# string of bools to select files
fb = None#[0, 1]


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
import itertools
import csv
import operator

pg.setConfigOption('background','w')
pg.setConfigOption('foreground','k')


def file_sorter(files):
    timestamps = [0] * len(files)        
    for ii, f in enumerate(files):
        temp = None
        for jj, ll in enumerate(f.split('_')):
            try:
                if temp:
                    timestamp = temp + float(ll)/100.
                    timestamps[ii] = timestamp
                    temp = None
                else:
                    temp = int(ll)
            except ValueError:
                temp = None
    return [f for (t, f) in sorted(zip(timestamps, files))]
         
                
                

def most_common(L):
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]

def get_labels(f):
    """Retrieve data file's comment"""
    with open(f, 'r') as fff:
        labels = next(itertools.islice(csv.reader(fff), 2, None))
    return labels
    
def get_f_labels(f):
    labels = get_labels(f)
    f_labels = [''] * 3
    ii = 0
    for label in labels:
        print label
        if 'Frequency' in label:
            label_list = label.strip(' ').split(' ')
            print label_list
            for ll in label_list:
                print ll
                if 'Hz' in ll and ll.strip('[').strip(']') == ll:
                    print ll
                    f_labels[ii] = ll
                    ii += 1
    return f_labels

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
        if '_sorted' in f.lower() and not 'roomtemp' in f.lower():
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
    global p4a, p4
    p4a.setGeometry(p4.getViewBox().sceneBoundingRect())
    p4a.linkedViewChanged(p4.getViewBox(), p4a.XAxis)
    
def update():
    global path, files_to_use, c_curves, l_curves, ct_curves, lt_curves, T_curves
    data = load_data(path, files_to_use)
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
    TBs = [data[:, 2], data[:, 9+o], data[:, 16+o+o]]
    Cs = [data[:, 3], data[:, 10+o], data[:, 17+o+o]]
    Ls = [data[:, 4], data[:, 11+o], data[:, 18+o+o]]
    
    for curve, t, C in zip(ct_curves, ts, Cs):
        curve.setData(x=t, y=C)
    for curve, t, L in zip(lt_curves, ts, Ls):
        curve.setData(x=t, y=L)
    for curve, T, C in zip(c_curves, Ts, Cs):
        curve.setData(x=T, y=C)
    for curve, T, L in zip(l_curves, Ts, Ls):
        curve.setData(x=T, y=L)
    data = np.column_stack((np.concatenate(ts),
                            np.concatenate(Ts),
                            np.concatenate(TBs)))
    data = np.array(sorted(data, key=lambda row: row[0]))
    for ii, curve in enumerate(T_curves):
        curve.setData(x=data[:, 0], y=data[:, ii+1])
    
if __name__ == '__main__':
    path, base_path, date = get_path(date)
    files = get_files(date, file_bool=fb)
    
    title = "Live Plotting %s/%s/%s" % date
    app = pg.QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Live Plotting")
    win.resize(1900, 1000)
    win.setWindowTitle(title)
        
    # enable antialiasing
    pg.setConfigOptions(antialias=True)
        
    p1 = win.addPlot(title=title, row=0, col=0)
    p1.setLabel('left', 'Capacitance (pF)')
    p1.setLabel('bottom', 'Temperature (K)')
    p1.addLegend()
    
    p2 = win.addPlot(title='', row=1, col=0)
    p2.setLabel('left', 'Loss Tangent')
    p2.setLabel('bottom', 'Temperature (K)')
    p2.addLegend()
    
    p2.setXLink(p1)
    
    p3 = win.addPlot(title='',
                     axisItems={'bottom':DateAxisItem.DateAxisItem('bottom')},
                                row=0, col=1)
    p3.setLabel('left', 'Temperature (K)')
    p3.addLegend()

    p4 = win.addPlot(title='',
                     axisItems={'bottom':DateAxisItem.DateAxisItem('bottom')},
                                row=1, col=1)
    p4.setLabel('left', 'Capacitance (pF)')
    p4.showAxis('right')
    p4.setLabel('right', 'Loss Tangent')
    
    p4a = pg.ViewBox()
    p4.scene().addItem(p4a)
    p4.getAxis('right').linkToView(p4a)
    p4a.setXLink(p4)
    p3.setXLink(p4)

    """comments = [''] * len(files)    
    for ii, f in enumerate(files):
        comments[ii] = sort_comments.get_comment(os.path.join(path, f))"""
                    
    #p3.setLabel('bottom', 'Temperature (K)')
    #p4.addLegend()
                    
    #p.showAxis('right')
    #p.setLabel('right', 'Loss Tangent')
    colors6 = [(204, 0, 0),    # dark red
               (76, 153, 0),   # dark green
               (0, 0, 204),    # dark blue
               (255, 128, 0),  # orange
               (0, 204, 204),  # cyan
               (153, 51, 255)] # purple
    colors2 = [(255, 0, 0), (0, 0, 255)]
    pens6 = [''] * len(colors6)
    pens2 = [''] * len(colors2)
    for ii, color in enumerate(colors6):
        pens6[ii] = pg.mkPen(color, width=2)
    for ii, color in enumerate(colors2):
        pens2[ii] = pg.mkPen(color, width=2)
    c_curves = [''] * 3
    l_curves = [''] * 3
    ct_curves = [''] * 6
    lt_curves = [''] * 3
    #labels = ['10kHz', '1kHz', '100Hz']
    #labels = ['20kHz', '2kHz', '400Hz']
    flabels = [''] * len(files)
    for ii, f in enumerate(files):
        flabels[ii] = get_f_labels(os.path.join(path, f))
    #print flabels
    labels = most_common(flabels)
    #fbool2 = [0] * len(files)
    #for ii, label in enumerate(flabels):
    #    print ii
    #    if label == labels:
    #        fbool2[ii] = 1
    #files_to_use = [''] * sum(fbool2)
    #ii = 0
    #for jj, bb in enumerate(fbool2):
    #    if bb:
    #        files_to_use[ii] = files[jj]
    files_to_use = file_sorter(files)
            
    for ii, label in enumerate(labels):
        c_curves[ii] = p1.plot(pen=pens6[ii], name=label)
        l_curves[ii] = p2.plot(pen=pens6[ii+3], name=label)
        ct_curves[ii] = p4.plot(pen=pens6[ii], name=label+' capacitance')
        ct_curves[ii+3] = p4.plot(pen=pens6[ii+3], name=label+' loss')
        lt_curves[ii] = pg.PlotCurveItem(pen=pens6[ii+3], name=label)
        p4a.addItem(lt_curves[ii])
    
    T_curves = [''] * 2
    labels = ['Stage A', 'Stage B']
    for ii, label in enumerate(labels):
        T_curves[ii] = p3.plot(pen=pens2[ii], name=label)

    updateViews()
    p4.getViewBox().sigResized.connect(updateViews)
    
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)
    pg.QtGui.QApplication.instance().exec_()       
    
    
                  
        

    