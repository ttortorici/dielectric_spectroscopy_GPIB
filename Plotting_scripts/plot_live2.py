# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore
import numpy as np
import pyqtgraph as pg
import sys
import calendar
import itertools
import data_files
import os
import csv
import time
import datetime
import numpy as np
import sys
import yaml
sys.path.append('../GPIB')
import get


def get_comment(f):
    global path
    """Retrieve data file's comment"""
    with open(os.path.join(path, f), 'r') as ff:
        comment_list = next(itertools.islice(csv.reader(ff), 1, None))[0].strip('# ').split('... ')
    comment = comment_list[0]
    for c in comment_list[-1:]:
        comment += '; %s' % c
    return comment

def count_rows(f):
    global path
    """Return the number of rows in a file"""
    return sum(1 for line in open(os.path.join(path, f), 'r'))


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

if 'min' in time_axis.lower():
    time_factor = 60
elif 'hr' in time_axis.lower():
    time_factor = 60 * 60
else:
    raise ValueError('time_axis has an invalid value')

"""establish the day data is getting taken"""
date = str(datetime.date.today()).split('-')
year = date[0]
month = date[1]
day = date[2]

"""replace date with sys.argv entry"""
if len(sys.argv) >= 2:
    datemsg = sys.argv[1].split('-')
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

"""make sure the numbers come out right"""
if len(day) == 1:
    day = '0' + day
if len(month) == 1:
    month = '0' + month
if len(year) == 2:
    year = '20' + year

"""get filepath in googledrive"""
base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
path = os.path.join(base_path, year, month, day)

"""get list of files in this directory"""
filenames_all = data_files.file_name(month, day, year)
filenames = []
for f in filenames_all[0]:
    if not '_sorted' in f.lower():
        filenames.append(f)
print 'All the files in the directory: ' + str(filenames)

"""Get presets"""
with open(os.path.join(base_path, 'presets_plotting.yml'), 'r') as f:
    preset = yaml.load(f)
cap_str_low = preset['cap'][0]
cap_str_high = preset['cap'][1]
loss_str_low = preset['loss'][0]
loss_str_high = preset['loss'][1]

params = [
        {'name': 'Data files to use from %s/%s/%s' % (month, day, year), 'type': 'group', 'children': []},
        {'name': 'Plotting parameters', 'type': 'group', 'children': [
                {'name': 'x-axis', 'type': 'list', 'values': ['temperature', 'time'], 'value': 'Temperature'},
                {'name': 'y-axis 0', 'type': 'list', 'values': ['loss', 'capacitance', 'temperature', 'voltage'], 'value': 'loss'},
                {'name': 'y-axis 1', 'type': 'list', 'values': ['loss', 'capacitance', 'temperature', 'voltage', 'none'], 'value': 'none'},
                {'name': 'y-axis 2', 'type': 'list', 'values': ['loss', 'capacitance', 'temperature', 'voltage', 'none'], 'value': 'none'},
                {'name': 'y-axis 3', 'type': 'list', 'values': ['loss', 'capacitance', 'temperature', 'voltage', 'none'], 'value': 'none'}
                ]
        }
    ]

for ii, f in enumerate(filenames):
    comment = get_comment(f)       # grab comment from the file
    flength = count_rows(f)
    name = '_'.join(f.split('_')[:-2])
    params[0]['children'].append('%s -- %s -- %s rows' % (name, comment, flength))
    
    
#app = pg.QtGui.QApplication([])
#import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType


## Create tree of Parameter objects
p = Parameter.create(name='params', type='group', children=params)

## If anything changes in the tree, print a message
def change(param, changes):
    print("tree changes:")
    for param, change, data in changes:
        path = p.childPath(param)
        if path is not None:
            childName = '.'.join(path)
        else:
            childName = param.name()
        print('  parameter: %s'% childName)
        print('  change:    %s'% change)
        print('  data:      %s'% str(data))
        print('  ----------')
    
p.sigTreeStateChanged.connect(change)


def valueChanging(param, value):
    print("Value changing (not finalized): %s %s" % (param, value))
    
# Too lazy for recursion:
for child in p.children():
    child.sigValueChanging.connect(valueChanging)
    for ch2 in child.children():
        ch2.sigValueChanging.connect(valueChanging)
        


def save():
    global state
    state = p.saveState()
    
def restore():
    global state
    add = p['Save/Restore functionality', 'Restore State', 'Add missing items']
    rem = p['Save/Restore functionality', 'Restore State', 'Remove extra items']
    p.restoreState(state, addChildren=add, removeChildren=rem)
p.param('Save/Restore functionality', 'Save State').sigActivated.connect(save)
p.param('Save/Restore functionality', 'Restore State').sigActivated.connect(restore)


## Create two ParameterTree widgets, both accessing the same data
t = ParameterTree()
t.setParameters(p, showTop=False)
t.setWindowTitle('pyqtgraph example: Parameter Tree')

win = pg.QtGui.QWidget()
layout = pg.QtGui.QGridLayout()
win.setLayout(layout)
layout.addWidget(pg.QtGui.QLabel("These are two views of the same data. They should always display the same values."), 0,  0, 1, 2)
layout.addWidget(t, 1, 0, 1, 1)
win.show()
win.resize(800,800)

## test save/restore
s = p.saveState()
p.restoreState(s)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.instance().exec_()
""""""



"""
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title="Basic array plotting", y=np.random.normal(size=100))

p2 = win.addPlot(title="Multiple curves")
p2.plot(np.random.normal(size=100), pen=(255,0,0), name="Red curve")
p2.plot(np.random.normal(size=110)+5, pen=(0,255,0), name="Green curve")
p2.plot(np.random.normal(size=120)+10, pen=(0,0,255), name="Blue curve")

p3 = win.addPlot(title="Drawing with points")
p3.plot(np.random.normal(size=100), pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')


win.nextRow()

p4 = win.addPlot(title="Parametric, grid enabled")
x = np.cos(np.linspace(0, 2*np.pi, 1000))
y = np.sin(np.linspace(0, 4*np.pi, 1000))
p4.plot(x, y)
p4.showGrid(x=True, y=True)

p5 = win.addPlot(title="Scatter plot, axis labels, log scale")
x = np.random.normal(size=1000) * 1e-5
y = x*1000 + 0.005 * np.random.normal(size=1000)
y -= y.min()-1.0
mask = x > 1e-15
x = x[mask]
y = y[mask]
p5.plot(x, y, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))
p5.setLabel('left', "Y Axis", units='A')
p5.setLabel('bottom', "Y Axis", units='s')
p5.setLogMode(x=True, y=False)

p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='y')
data = np.random.normal(size=(10,1000))
ptr = 0
def update():
    global curve, data, ptr, p6
    curve.setData(data[ptr%10])
    if ptr == 0:
        p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)


win.nextRow()

p7 = win.addPlot(title="Filled plot, axis disabled")
y = np.sin(np.linspace(0, 10, 1000)) + np.random.normal(size=1000, scale=0.1)
p7.plot(y, fillLevel=-0.3, brush=(50,50,200,100))
p7.showAxis('bottom', False)


x2 = np.linspace(-100, 100, 1000)
data2 = np.sin(x2) / x2
p8 = win.addPlot(title="Region Selection")
p8.plot(data2, pen=(255,255,255,200))
lr = pg.LinearRegionItem([400,700])
lr.setZValue(-10)
p8.addItem(lr)

p9 = win.addPlot(title="Zoom on selected region")
p9.plot(data2)
def updatePlot():
    p9.setXRange(*lr.getRegion(), padding=0)
def updateRegion():
    lr.setRegion(p9.getViewBox().viewRange()[0])
lr.sigRegionChanged.connect(updatePlot)
p9.sigXRangeChanged.connect(updateRegion)
updatePlot()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.instance().exec_()"""
