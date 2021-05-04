# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 13:48:49 2017

@author: Chuck
"""
import os
import sys
sys.path.append('../GPIB')
import get
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
import DateAxisItem
import datetime
import time
import data_files


class Window(object):  
    
    def __init__(self, titles=None, xlabels=None, ylabels=None, xdatas=None, 
                 ydatas=None, yaxes=None, date=None, file_bool=None):
        #pg.setConfigOption('background','w')
        #pg.setConfigOption('foreground','k')
        self.titles = titles
        self.xlabels = xlabels
        self.ylabels = ylabels
        self.xdatas = xdatas
        self.ydatas = ydatas
        self.yaxes = yaxes
        
        """set date"""
        current_date = str(datetime.date.today()).split('-')
        self.year = current_date[0]
        self.month = current_date[1]
        self.day = current_date[2]
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
        # make sure the numbers come out right
        if len(self.day) == 1:
            self.day = '0' + self.day
        if len(self.month) == 1:
            self.month = '0' + self.month
        if len(self.year) == 2:
            self.year = '20' + self.year
            
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data',
                                      'Teddy')
        self.path = os.path.join(self.base_path, self.year, self.month,
                                 self.day)
        
        """get list of files in this directory"""
        filenames = data_files.file_name_sorted(self.month, self.day, self.year)
        self.filenames = []
        for f in filenames[0]:
            if '_sorted' in f.lower():
                self.filenames.append(f)
        print 'All the files in the directory: ' + str(self.filenames)
        
        """use file_bool to select files"""
        if file_bool:
            if len(self.filenames) < len(file_bool):
                file_bool = file_bool[:len(self.filenames)]
            self.files_to_use = []
            for ii, b in enumerate(file_bool):
                if b:
                    self.files_to_use.append(self.filenames[ii])
        else:
            self.files_to_use = self.filenames
        print self.files_to_use
                    
        title = "Live Plotting %s/%s/%s" % (self.month, self.day, self.year)
        self.app = pg.QtGui.QApplication([])
        self.win =pg.GraphicsWindow(title="Live Plotting")
        self.win.resize(1000, 600)
        self.win.setWindowTitle(title)
        
        # enable antialiasing
        pg.setConfigOptions(antialias=True)
        
                  
        
        self.plotlist = []
        self.curvelist = []
        self.curvenum = []
        self.plotnum = len(self.plotlist)
        
    def plot6(self):
        self.plotnum = len(self.titles)
        self.plotlist = [''] * self.plotnum
        self.curvelist = [[]] * self.plotnum
        self.curvenum = [''] * self.plotnum
        
        for ii, title, xlabel, ylabel, xdata, ydata, yaxis in zip(xrange(len(self.titles)), self.titles, self.xlabels, self.ylabels, self.xdatas, self.ydatas, self.yaxes):
            p = self.win.addPlot(title=title)
            
            for yax in yaxis:
                if yax.upper() == 'L':
                    p.setLabel('left', ylabel[0])
                    p2 = None
                elif yax.upper() == 'R':
                    p2 = pg.ViewBox()
                    p.scene().addItem(p2)
                    p.getAxis('right').linkToView(p2)
                    p2.setXLink(p)
                    p.setLabel('right', ylabel[1])
            p.setLabel('bottom', xlabel)
            p.showAxis('right')
            #print xlabel
            count = 0
            for d, yax in zip(ydata, yaxis):
                if ('capacitance' in title.lower()) or ('loss' in title.lower()):
                    curves = 3
                if 'labjack' in title.lower():
                    curves = 4
                else:
                    curves = 1
                for _ in xrange(curves):
                    if yax.upper() == 'L':
                        c = p.plot(pen=(count, len(ydata)*curves))
                    elif yax.upper() == 'R':
                        c = pg.PlotCurveItem(pen=(count, len(ydata)*curves))
                        p2.addItem(c)
                        self.update_views(p, p2)
                        p.getViewBox().sigResized.connect(self.update_views)
                    count += 1
                    #print 'bbbb'
                    #print ii
                    self.curvelist[ii].append(c)
                    self.curvenum[ii] = len(self.curvelist[ii])
            if ii % 2:      # if ii is odd
                self.win.nextRow()
            if p2:
                self.plotlist[ii] = [p, p2]
            else:
                self.plotlist[ii] = [p]
                
        print self.plotlist
        print self.curvelist
        print self.curvenum
        print self.plotnum
        
    def update_views(self, p, p2):
        p2.setGeometry(p.getViewBox().sceneBoundingRect())
        p2.linkedViewChanged(p.getViewBox(), p2.XAxis)
        
    def addPlot(self, title=''):
        self.plotlist.append(win.addPlot(title=title))
        self.curvelist.append([])
        self.curvenum.append(0)
        self.plotnum = len(self.plotlist)

    def addCurve(self, plotnum, curve_max=5):
        pen = self.curvenum[plotnum]
        c = self.plotlist[plotnum].plot(pen=(pen, curve_max))
        self.curvelist[plotnum].append(c)
        self.curvelist[plotnum][self.curvenum[plotnum]]
        self.curvenum[plotnum] = len(self.curvelist[plotnum])
    
    def addPlots(self):
        self.p = {}
        for title in self.titles:
            self.p[title] = self.win.addPlot(title=title)
    
    def updateplot(self):
        #print 'up1'
        self.loaddata()
        #print 'loaded'
        for ii, xd, yd, yax, pp, cl, cn in zip(xrange(self.plotnum), self.xdatas, self.ydatas, self.yaxes, self.plotlist, self.curvelist, self.curvenum):
            #print xd
            if xd == 'TA':
                xs = self.TA
            elif xd == 'TA_tot':
                xs = [self.TA_tot]
            elif xd == 't_tot':
                xs = [self.t_tot]
            elif xd == 't':
                xs = self.t
            #for jj, p in enumerate(pp):   
            for ydi in yd:
                if ydi == 'cap':
                    ys = self.C
                elif ydi == 'loss':
                    ys = self.L
                elif ydi == 'TA_tot':
                    ys = [self.TA_tot]
                elif ydi == 'TB_tot':
                    ys = [self.TB_tot]
                elif ydi == 'lj':
                    ys = self.V_tot
                
                count = len(ys) * ii
                for jj, x, y in zip(xrange(len(ys)), xs, ys):
                    #print y
                    cl[count].setData(x=x, y=y)
                    count += 1
        print 'updated'
                    
    
    def run(self):
        self.plot6()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        print 'start'
        self.timer.timeout.connect(self.updateplot)
        self.timer.start()
        print 'timer start'
        pg.QtGui.QApplication.instance().exec_()        
        #self.app.exec_()
        #self.app.exec_()
        
    def loaddata_min(self):
        skip = 0
        #print skip
        temp_skip = -1
        #print temp_skip
        while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
            temp_skip = skip
            #print 'trying'            
            try:
                data = np.loadtxt(os.path.join(self.path,
                                               self.files_to_use[0]),
                                  comments='#', delimiter=',', skiprows=4)
                #print 'passed'
            except StopIteration:
                skip += 1
                #print 'failed'
        if len(self.files_to_use) > 1:
            for ii, f in enumerate(self.files_to_use[1:]):
                try:
                    data_temp = np.loadtxt(os.path.join(self.path, f),
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
        
    def plot_capacitance_vs_temperature(self):
        self.titles = ['Capacitance vs Temperature']
        self.xlabels = ['Temperature (K)']
        self.ylabels = ['Capacitance (pF)']
        self.xdatas = ['TA']
        self.ydatas = [['cap']]
        self.yaxes = [['L']]
        self.run()
        
    def loaddata(self):
        """Load the selected data files"""
        #print 'loading data'
        # all this skip nonsense is a work around so the code will ignore
        # "empty" files
        skip = 0
        #print skip
        temp_skip = -1
        #print temp_skip
        while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
            temp_skip = skip
            #print 'trying'            
            try:
                data = np.loadtxt(os.path.join(self.path,
                                               self.files_to_use[0]),
                                  comments='#', delimiter=',', skiprows=4)
                #print 'passed'
            except StopIteration:
                skip += 1
                #print 'failed'
        if len(self.files_to_use) > 1:
            for ii, f in enumerate(self.files_to_use[1:]):
                try:
                    data_temp = np.loadtxt(os.path.join(self.path, f),
                                           comments='#', delimiter=',',
                                           skiprows=4)
                    try:
                        data = np.append(data, data_temp, axis=0)
                    except ValueError:
                        data = np.append(data, np.array([data_temp]), axis=0)
                except StopIteration:
                    pass
        #print np.shape(data)
        columns = np.shape(data)[1]
        if columns == 21:
            o = 0
        elif columns == 24:
            o = 1
        elif columns == 36:
            o = 4
        #print o
        self.t = [data[:, 0], data[:, 7+o], data[:, 14+o+o]]
        self.TA = [data[:, 1], data[:, 8+o], data[:, 15+o+o]]
        TB = [data[:, 2], data[:, 9+o], data[:, 16+o+o]]
        self.C = [data[:, 3], data[:, 10+o], data[:, 17+o+o]]
        self.L = [data[:, 4], data[:, 11+o], data[:, 18+o+o]]
        self.mv = [data[:, 5], data[:, 12+o], data[:, 19+o+o]]
        self.fr = [data[0, 6+o], data[0, 13+o+o], data[0, 20+o+o+o]]
        t_tot = np.concatenate(self.t)
        TA_tot = np.concatenate(self.TA)
        TB_tot = np.concatenate(TB)
        data_tot = np.column_stack((t_tot, TA_tot, TB_tot))
        if o:
            self.V = [[]] * o
            for ii in xrange(o):
                self.V[ii] = [data[:, 6+ii], data[:, 14+o-1+ii], data[:, 22+o+o-2+ii]]
            V_tot = [[]] * o
            self.V_tot = [[]] * o
            for ii, v in enumerate(self.V):
                V_tot[ii] = np.concatenate(v)
                data_tot = np.column_stack((data_tot, V_tot[ii]))
        else:
            self.V = None
            self.V_tot = None
        data_tot = np.array(sorted(data_tot, key=lambda entry:entry[0]))
        self.t_tot = data_tot[:, 0]
        self.TA_tot = data_tot[:, 1]
        self.TB_tot = data_tot[:, 2]
        if self.V:
            for ii in xrange(o):
                self.V_tot[ii] = data_tot[:, 3+ii]
        #print 'loaded'
    
    
        
        
if __name__ == "__main__":
    titles = ['Capacitance vs Temperature']
    xlabels = ['Temperature (K)']
    ylabels = [['Capacitance (pF)']]
    xdatas = ['TA']
    ydatas = [['cap']]
    yaxes = [['L']]
    titles = ['Capacitance vs Temperature',
              'Temperatures vs Time',
              'Loss vs Temperature',
              'Capacitance and Loss vs Time',
              'Labjack vs Temperature',
              'Labjack vs Time']
    xlabels = ['Temperature (K)',
               'Time',
               'Temperature (K)',
               'Time',
               'Temperature (K)',
               'Time']
    ylabels = [['Capacitance (pF)'],
               ['Temperature (K)'],
               ['Loss Tangent'],
               ['Capacitance (pF)', 'Loss Tangent'],
               ['Labjack (V)'],
               ['Labjack (V)']]
    xdatas = ['TA',
              't_tot',
              'TA',
              't',
              'TA_tot',
              't_tot']
    ydatas = [['cap'],
              ['TA_tot', 'TB_tot'],              
              ['loss'],              
              ['cap', 'loss'],
              ['lj'],
              ['lj']]
    yaxes = [['L'],
             ['L', 'L'],
             ['L'],
             ['L', 'R'],
             ['L'],
             ['L']]
    win = Window(titles, xlabels, ylabels, xdatas, ydatas, yaxes)
    win.plot_capacitance_vs_temperature()


        
"""# Set File path
path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', '2017',
                    '07', '14')

# Fetch most recent file in path
name = 'Calibration_bare_1500064809_79_sorted.csv'
 
fname = os.path.join(path, name)

data = np.loadtxt(fname, comments='#', delimiter=',', skiprows=4)

win = pg.GraphicsWindow()
win.setWindowTitle(sys.argv[0])
win.setWindowIcon(pg.QtGui.QIcon('quickplot_icon.png'))

label = pg.LabelItem(justify='right')
win.addItem(label)
label.setText('hello')
axB = DateAxisItem.DateAxisItem('bottom')
axL = pg.AxisItem('left')
axR = pg.AxisItem('right')
p = win.addPlot(axisItems={'bottom':axB, 'left': axL, 'right': axR},
                row=1, col=0)
plotlist = [];
p.addLegend()

namelist = ['Stage A [K]',
            'Stage B [K]',
            'Capacitance [pF] 10kHz',
            'Loss 10kHz',
            'Capacitance [pF] 1kHz',
            'Loss 1kHz',
            'Capacitance [pF] 100Hz',
            'Loss 100Hz',
            'DC voltage [V]']
for ii in xrange(len(namelist)):
    
    pp = p.plot(pen=(ii, len(namelist)),name=namelist[ii])
    plotlist.append(pp)

vLine = pg.InfiniteLine(angle=90, movable=False)
#hLine = pg.InfiniteLine(angle=0, movable=False)
p.addItem(vLine, ignoreBounds=True)
#p.addItem(hLine, ignoreBounds=True)


vb = p.vb

def mouseMoved(evt):
    global label,data
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if p.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
	#index = np.where(data[:,0]==mousePoint.x())
	index2 = np.where(data[:,0]>=mousePoint.x())
	#print len(index2),len(index2[0])
	if len(index2[0])>0:
	  index = index2[0][0]
	else:
	  index = -1
        #index = int(mousePoint.x())
	if index > 0 and index < len(data[:,1]):
          #label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data[index,1], data[index,2]))
	  msgout = "%s, %8.2f %8.2f %8.2f %8.2f %8.3f" % (time.ctime(mousePoint.x()), data[index,2], data[index,3],data[index,4], data[index,5], data[index,1])
          label.setText(msgout)
	  #print msgout
 
	#print mousePoint.x(), data[index,0],data[index,1]
        vLine.setPos(mousePoint.x())
        #hLine.setPos(mousePoint.y())
proxy = pg.SignalProxy(p.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

offset = 0
if len(sys.argv)>1:
  offset = int(sys.argv[1])

def update():
    global plotlist, fname, offset
    data = np.loadtxt(fname, comments='#', delimiter=',', skiprows=4)
    for idx, pp in enumerate(plotlist):
        if idx in [0, 1, 8]:
            t = np.concatenate((data[offset:, 0], data[offset:, 7], data[offset:, 14]))
            ii = int(idx/2+1)
            y = np.concatenate((data[offset:, 1+ii], data[offset:, 8+ii], data[offset:, 15+ii]))
            data_set = np.column_stack((t, y))
            data_set = np.array(sorted(data_set, key=lambda entry: entry[0]))
        elif idx in [2, 3]:
            t = data[offset:, 0]
            y = data[offset:, idx+1]
        elif idx in [4, 5]:
            t = data[offset:, 7]
            y = data[offset:, idx+6]
        elif idx in [6, 7]:
            t = data[offset:, 14]
            y = data[offset:, idx+11]
        pp.setData()
    
        pp.setData(t, y)
        
def update33():
    global plotlist, fname, offset
    print 'update'
    data = np.loadtxt(fname, comments='#', delimiter=',', skiprows=4)
    t = np.concatenate((data[offset:, 0], data[offset:, 7], data[offset:, 14]))
    t = np.array(sorted(t))
    print t
    for idx, pp in enumerate(plotlist):
        y = (t-t[0])*idx
        pp.setData()
    
        pp.setData(t, y)
print 'go'
  
timer = QtCore.QTimer()
timer.setInterval(10000)
print 'start'
timer.timeout.connect(update)
timer.start()
app.exec_()
app.exec_()"""