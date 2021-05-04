# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with
the left/right mouse buttons. Right click on any plot to show a context menu.
"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import DateAxisItem
import time


class SinglePlot:
    def __init__(self, x, y, pen, name, ax):
        self.x = x
        self.y = y
        self.pen = pen
        self.name = name
        self.ax = ax


class Graph:
    def __init__(self, title='', axes_labels=['', ''], plot_size=(1200, 900)):
        """A class for a single plot, can take 3 items for axes_labels to make a axis on the the right y axis.
        plotL plots things against the left y axis and plotR plots things against the right y axis"""
        self.axis_pen = pg.mkPen(color=(0, 0, 0), width=3)
        self.title = title
        self.axes_labels = axes_labels

        # set background colors
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # QtGui.QApplication.setGraphicsSystem('raster')
        self.app = QtGui.QApplication([])
        # mw = QtGui.QMainWindow()
        # mw.resize(800,800)
        self.win = pg.GraphicsWindow(title=title)
        self.win.resize(plot_size[0], plot_size[1])
        self.win.setWindowFilePath(title)
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        # self.label = pg.LabelItem(justify='right')
        # self.win.addItem(self.label)
        # self.label.setText('Hi')
        # self.vLine = pg.InfiniteLine(angle=90, movable=False)
        if len(self.axes_labels) == 3:
            # self.ax1 = DateAxisItem.DateAxisItem('bottom')
            # self.ax2 = DateAxisItem.DateAxisItem('top')
            self.plotL = self.win.addPlot(title=self.title,  # axisItems={'bottom': self.ax1},
                                          row=0, col=0)
            # create label on right axes for temperature
            self.plotL.setLabels(left='<font size="20">%s</font>' % self.axes_labels[1])
            self.plotL.setLabels(bottom='<font size="20">%s</font>' % self.axes_labels[0])
            self.plotR = pg.ViewBox()
            self.plotL.showAxis('right')
            self.plotL.scene().addItem(self.plotR)
            self.plotL.getAxis('right').linkToView(self.plotR)
            self.plotR.setXLink(self.plotL)
            self.plotL.getAxis('right').setLabel('<font size="20">%s</font>' % self.axes_labels[2], color='#000000')
        else:
            self.plotL = self.win.addPlot(title=self.title, row=0, col=0)
            self.plotL.setLabels(left='<font size="20">%s</font>' % self.axes_labels[1])
            self.plotL.setLabels(bottom='<font size="20">%s</font>' % self.axes_labels[0])
            self.plotL.setLabels(right='')
        for dir in ['top', 'bottom', 'left', 'right']:
            self.plotL.getAxis(dir).setPen(self.axis_pen)
            self.plotL.getAxis(dir).maxTicklength = -10
            self.plotL.getAxis(dir).setTickFont(QtGui.QFont('Ubuntu', 20))
        self.plotL.getAxis('left').setWidth(150)
        #self.plotL.getAxis('bottom').setHeight(100)
        self.plotL.setLabels(top='')
        self.plotL.setTitle('<font size="20">%s</font>' % title)
        # self.plotL.tickFont = QtGui.QFont().setPixelSize(100)
        # self.plotL.getAxis('left').setPen(self.font_pen)
        # self.plotL.getAxis('bottom').setPen(self.font_pen)
        # self.plotL.getAxis('top').setPen(self.font_pen)
        self.plotL.addLegend()
        self.plotlistL1 = []
        self.plotlistL2 = []
        self.plotlistR = []

    def logy(self, on):
        self.plotL.setLogMode(y=on)

    def logx(self, on):
        self.plotL.setLogMode(x=on)

    def loglog(self, on):
        self.plotL.setLogMode(on, on)

    def range(self, min, max):
        self.plotL.getAxis('bottom').setRange(min, max)

    def grid(self, on, op=0.5):
        if on:
            self.plotL.showGrid(True, True, op)
        else:
            self.plotL.showGrid(False, False)

    def plot(self, x, y, pen=pg.mkPen(color='r', width=4, style=QtCore.Qt.DashLine), name='', ax='L'):
        """plot something on the graph"""
        p2 = SinglePlot(x, y, pen, name, ax)
        if 'R' in ax.upper():
            self.plotR.addItem(pg.PlotCurveItem(x, y, pen=pen))
            self.plotL.plot([x[0]], [y[0]], pen=pen, name=name)
            self.plotlistR.append(p2)
        elif 'L' in ax.upper():
            p1 = self.plotL.plot(x, y, pen=pen, name=name)
            self.plotlistL1.append(p1)
            self.plotlistL2.append(p2)

    def plot_sep_freq(self, x, y, freqs, ax='L'):
        """plot something separating frequencies"""
        pen = [pg.mkPen(color='k', width=4, style=QtCore.Qt.SolidLine),
               pg.mkPen(color='r', width=4, style=QtCore.Qt.SolidLine),
               pg.mkPen(color='b', width=4, style=QtCore.Qt.SolidLine)]
        frequencies_unique = np.sort(np.unique(freqs))
        freq_locs = {}
        for freq in frequencies_unique:
            freq_locs[str(freq)] = np.where(freqs == freq)
        for ii, freq in enumerate(frequencies_unique):
            self.plot(x[freq_locs[str(freq)]], y[freq_locs[str(freq)]], pen=pen[ii], name='%d Hz' % freq, ax=ax)

    def updateViews(self):
        """Handle view resizing"""
        # view has resized; update auxiliary views to match
        self.plotR.setGeometry(self.plotL.vb.sceneBoundingRect())
        """need to re-update linked axes since this was called
           incorrectly while views had different shapes.
           (probably this should be handled in ViewBox.resizeEvent)"""
        self.plotR.linkedViewChanged(self.plotL.vb, self.plotR.XAxis)

    def update(self):
        if len(self.plotlistR) > 0:
            self.updateViews()
        #for ii, p1, p2 in zip(xrange(len(self.plotlistL1)), self.plotlistL1, self.plotlistL2):
        #    p1.setData(p2.x, p2.y)
        #for ii in xrange(len(self.plotlistR)):
        #    p = self.plotlistR[ii]
        #    self.plot(p.x, p.y, pen=p.pen, name=p.name, ax=p.ax)
        #    print 'plotted right ax ' + str(ii)

    def show(self):
        self.update()
        legendLabelStyle = {'color': (0, 0, 0), 'size': '16pt', 'bold': False, 'italic': False}
        for item in self.plotL.legend.items:
            for single_item in item:
                if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
                    single_item.setText(single_item.text, **legendLabelStyle)
        self.win.raise_()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50000)
        self.timer.timeout.connect(self.update)
        self.timer.start(1)
        self.app.exec_()
        time.sleep(1)
        self.app.exec_()


def load_data(file_path, file_names):
    data = np.loadtxt(os.path.join(file_path, file_names[0]), comments='#', delimiter=',', skiprows=3)
    if len(file_names) > 1:
        for ii, f in enumerate(file_names[1:]):
            data_temp = np.loadtxt(os.path.join(file_path, f), comments='#', delimiter=',', skiprows=3)
            try:
                data = np.append(data, data_temp, axis=0)
            except ValueError:
                data = np.append(data, np.array([data_temp]), axis=0)
    data = scrub_data(data)
    return data


def scrub_data(data_old):
    good_cap_data = np.where(data_old[:, 4] > 1.2)
    data_temp = data_old[good_cap_data]
    good_loss_data = np.where(np.logical_and(data_temp[:, 5] > 0, data_temp[:, 5] <= 1))
    data_new = data_temp[good_loss_data]
    return data_new

def plot_ctime():
    Cap_v_time = Graph('Capacitance vs Time', ['Time [min]', 'Capacitance [pF]', 'Temperature [K]'])
    Cap_v_time.plot_sep_freq(timestamps, capacitance, freqs)
    Cap_v_time.plot(timestamps, temperature1, pen=pg.mkPen(color='r', width=4, style=QtCore.Qt.DashDotDotLine),
                    name='Stage A Temperature', ax='R')
    Cap_v_time.plot(timestamps, temperature2, pen=pg.mkPen(color='b', width=4, style=QtCore.Qt.DashDotDotLine),
                    name='Stage B Temperature', ax='R')
    Cap_v_time.show()

def plot_ctemp():
    Cap_v_temp = Graph('Capacitance vs Temperature', ['Temperature [K]', 'Capactiance [pF]'])
    Cap_v_temp.plot_sep_freq(temperature1, capacitance, freqs)
    Cap_v_temp.grid(True)
    Cap_v_temp.show()

def plot_ltemp():
    Loss_v_temp = Graph('Loss vs Temperature', ['Temperature [K]', 'Loss Tangent'])
    Loss_v_temp.plot_sep_freq(temperature1, loss, freqs)
    Loss_v_temp.logy(True)
    Loss_v_temp.grid(True)
    Loss_v_temp.range(20, 400)
    Loss_v_temp.show()

if __name__ == '__main__':
    import data_files
    import os
    import datetime
    import sys;
    sys.path.append('../GPIB')
    import get

    date = str(datetime.date.today()).split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    if len(sys.argv) == 3:
        month = sys.argv[1]
        day = sys.argv[2]
    elif len(sys.argv) == 4:
        year = sys.argv[3]
        month = sys.argv[1]
        day = sys.argv[2]
    elif len(sys.argv) == 2:
        day = sys.argv[1]

    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
    filenames = data_files.file_name(month, day, year)

    data = load_data(filepath, filenames[0])

    timestamps = (data[:, 0] - data[0, 0]) / 60
    temperature1 = data[:, 1]
    temperature2 = data[:, 2]
    freqs = data[:, 3]
    capacitance = data[:, 4]
    loss = data[:, 5]

    plot_ltemp()

#class Plotter:
#    def __init__(self, path, data_file, plot_num, title='', plot_size=(1920, 1080)):
#        self.plot_num = plot_num
#        pg.setConfigOption('background', 'w')
#        pg.setConfigOption('foreground', 'k')
#        self.path = path
#        self.data_file = data_file
#        print os.path.join(path, data_file[0])
#        data = np.loadtxt(os.path.join(path, data_file[0]), comments='#', delimiter=',', skiprows=3)
#        if len(data_file) > 1:
#            for ii, f in enumerate(data_file[1:]):
#                data_temp = np.loadtxt(os.path.join(path, f), comments='#', delimiter=',', skiprows=3)
#                try:
#                    data = np.append(data, data_temp, axis=0)
#                except ValueError:
#                    data = np.append(data, np.array([data_temp]), axis=0)
#        self.data = data
#        self.scrub_data()
#        # QtGui.QApplication.setGraphicsSystem('raster')
#        self.app = QtGui.QApplication([])
#        # mw = QtGui.QMainWindow()
#        # mw.resize(800,800)
#        self.win = pg.GraphicsWindow(title=title)
#        self.win.resize(plot_size[0], plot_size[1])
#        self.win.setWindowFilePath(title)
#        # Enable antialiasing for prettier plots
#        pg.setConfigOptions(antialias=True)
#        self.get_frequency_locations()
#        self.plot_list = []
#        self.label = pg.LabelItem(justify='right')
#        #self.win.addItem(self.label)
#        #self.label.setText('Hi')
#        #self.vLine = pg.InfiniteLine(angle=90, movable=False)
#
#        self.colors = [(0, 0, 0),           # black
#                       (255, 0, 0),         # red
#                       (0, 0, 255),         # blue
#                       (100, 125, 255),     # soft green
#                       (255, 0, 235),       # yellow
#                       (255, 100, 80),      # light red
#                       (255, 0, 0)]         # red
#
#        if plot_num == 1:
#            # set up Capacitance vs Time
#            self.ax1 = DateAxisItem.DateAxisItem('bottom')
#            self.C_v_time = self.win.addPlot(title="Capacitance vs Time", axisItems={'bottom': self.ax1}, row=0, col=0)
#            self.C_v_time.setLabels(left='Capacitance [pF]')
#            self.C_v_time.setLabels(bottom='Time')
#            # create label on right axes for temperature
#            self.Temp_v_time1 = pg.ViewBox()
#            self.C_v_time.showAxis('right')
#            self.C_v_time.scene().addItem(self.Temp_v_time1)
#            self.C_v_time.getAxis('right').linkToView(self.Temp_v_time1)
#            self.Temp_v_time1.setXLink(self.C_v_time)
#            self.C_v_time.getAxis('right').setLabel('Temperature [K]', color='#000000')     # blue
#            self.C_v_time.addLegend()
#            self.plot_C_v_time(init=True)
#
#        elif plot_num == 2:
#            # set up Capacitance vs Temperature
#            self.C_v_Temp = self.win.addPlot(title="Capacitance vs Temperature", row=0, col=0)
#            self.C_v_Temp.setLabels(left='Capacitance [pF]')
#            self.C_v_Temp.setLabels(bottom='Temperature [K]')
#            self.C_v_Temp.addLegend()
#            self.plot_C_v_Temp(init=True)
#
#            #self.win.nextRow()      # start new row of graphs
#
#        elif plot_num == 3:
#            # set up Loss vs Time
#            self.ax2 = DateAxisItem.DateAxisItem('bottom')
#            self.L_v_time = self.win.addPlot(title="Loss vs Time", axisItems={'bottom': self.ax2}, row=0, col=0)
#            self.L_v_time.setLabels(left='Loss tangent')
#            self.L_v_time.setLabels(bottom='Time')
#            # create label on right axes for temperature
#            self.Temp_v_time2 = pg.ViewBox()
#            self.L_v_time.showAxis('right')
#            self.L_v_time.scene().addItem(self.Temp_v_time2)
#            self.L_v_time.getAxis('right').linkToView(self.Temp_v_time2)
#            self.Temp_v_time2.setXLink(self.L_v_time)
#            self.L_v_time.getAxis('right').setLabel('Temperature [K]', color='#000000')     # blue
#            #self.L_v_time.addLegend()
#            self.plot_L_v_time(init=True)
#
#        elif plot_num == 4:
#            # set up Loss vs Temp
#            self.L_v_Temp = self.win.addPlot(title="Loss vs Temperature", row=0, col=0)
#            self.L_v_Temp.setLabels(left='Loss Tangent')
#            self.L_v_Temp.setLabels(bottom='Temperature [K]')
#            self.L_v_Temp.addLegend()
#            self.plot_L_v_Temp(init=True)
#
#    def update(self):
#        data = np.loadtxt(os.path.join(self.path, self.data_file[0]), comments='#', delimiter=',', skiprows=3)
#        if len(self.data_file) > 1:
#            for ii, f in enumerate(self.data_file[1:]):
#                data_temp = np.loadtxt(os.path.join(self.path, f), comments='#', delimiter=',', skiprows=3)
#                try:
#                    data = np.append(data, data_temp, axis=0)
#                except ValueError:
#                    data = np.append(data, np.array([data_temp]), axis=0)
#        self.data = data
#        self.scrub_data()
#        self.updateViews()
#        if self.plot_num == 1:
#            self.plot_C_v_time()
#        elif self.plot_num == 2:
#            self.plot_C_v_Temp()
#        elif self.plot_num == 3:
#            self.plot_L_v_time()
#        elif self.plot_num == 4:
#            self.plot_L_v_Temp()
#
#    def updateViews(self):
#        """Handle view resizing"""
#        # view has resized; update auxiliary views to match
#        """need to re-update linked axes since this was called
#           incorrectly while views had different shapes.
#           (probably this should be handled in ViewBox.resizeEvent)"""
#        if self.plot_num == 1:
#            self.Temp_v_time1.setGeometry(self.C_v_time.vb.sceneBoundingRect())
#            self.Temp_v_time1.linkedViewChanged(self.C_v_time.vb, self.Temp_v_time1.XAxis)
#        elif self.plot_num == 3:
#            self.Temp_v_time2.setGeometry(self.L_v_time.vb.sceneBoundingRect())
#            self.Temp_v_time2.linkedViewChanged(self.L_v_time.vb, self.Temp_v_time2.XAxis)
#
#    def get_frequency_locations(self):
#        self.frequencies = np.sort(np.unique(self.data[:, 3]))
#        self.freq_locs = {}
#        for freq in self.frequencies:
#            self.freq_locs[str(freq)] = np.where(self.data[:, 3] == freq)
#
#    def plot_C_v_time(self, init=False):
#        if init == True:
#            p1 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
#                                                            pen=(0, 255, 0)))        # green
#            p2 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
#                                                            pen=(0, 180, 255)))  # cyan
#            self.C_v_time.plot([self.data[0, 0]], [self.data[0, 4]], pen=(0, 255, 0), name="Stage Temperature")
#            self.C_v_time.plot([self.data[0, 0]], [self.data[0, 4]], pen=(0, 180, 255),
#                               name="Transfer Stage Temperature")
#        else:
#            p1 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
#                                                            pen=(0, 255, 0), name="Stage Temperature"))  # cyan
#            p2 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
#                                                            pen=(0, 180, 255), name="Transfer Temperature"))  # cyan
#        self.temp_plotlist1 = [p1, p2]
#        self.Ctime_plotlist = []
#        for ii, freq in enumerate(self.frequencies):
#            if init == True:
#                pp = self.C_v_time.plot(self.data[:, 0][self.freq_locs[str(freq)]],
#                                        self.data[:, 4][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii], name="%d Hz" % freq)
#            else:
#                pp = self.C_v_time.plot(self.data[:, 0][self.freq_locs[str(freq)]],
#                                        self.data[:, 4][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii])
#
#            self.Ctime_plotlist.append(pp)
#
#    def plot_L_v_time(self, init=False):
#        if init == True:
#            p1 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
#                                                            pen=(0, 255, 0)))  # green
#            p2 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
#                                                            pen=(0, 180, 255)))  # cyan
#            self.L_v_time.plot([self.data[0, 0]], [self.data[0, 5]], pen=(0, 255, 0), name="Stage Temperature")
#            self.L_v_time.plot([self.data[0, 0]], [self.data[0, 5]], pen=(0, 180, 255),
#                               name="Transfer Stage Temperature")
#        else:
#            p1 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
#                                           pen=(0, 255, 0)))        # green
#            p2 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
#                                           pen=(0, 180, 255)))      # cyan
#        self.temp_plotlist2 = [p1, p2]
#        self.Ltime_plotlist = []
#        for ii, freq in enumerate(self.frequencies):
#            if init == True:
#                pp = self.L_v_time.plot(self.data[:, 0][self.freq_locs[str(freq)]],
#                                        self.data[:, 5][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii], name='%d Hz' % freq)
#            else:
#                pp = self.L_v_time.plot(self.data[:, 0][self.freq_locs[str(freq)]],
#                                        self.data[:, 5][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii])
#            self.Ltime_plotlist.append(pp)
#
#    def plot_C_v_Temp(self, init=False):
#        self.Ctemp_plotlist = []
#        for ii, freq in enumerate(self.frequencies):
#            if init == False:
#                pp = self.C_v_Temp.plot(self.data[:, 1][self.freq_locs[str(freq)]],
#                                        self.data[:, 4][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii])
#            else:
#                pp = self.C_v_Temp.plot(self.data[:, 1][self.freq_locs[str(freq)]],
#                                        self.data[:, 4][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii], name='%d Hz' % freq)
#            self.Ctemp_plotlist.append(pp)
#
#    def plot_L_v_Temp(self, init=False):
#        self.Ltemp_plotlist = []
#        for ii, freq in enumerate(self.frequencies):
#            if init == False:
#                pp = self.L_v_Temp.plot(self.data[:, 1][self.freq_locs[str(freq)]],
#                                        self.data[:, 5][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii])
#            else:
#                pp = self.L_v_Temp.plot(self.data[:, 1][self.freq_locs[str(freq)]],
#                                        self.data[:, 5][self.freq_locs[str(freq)]],
#                                        pen=self.colors[ii], name='%d Hz' % freq)
#            self.Ltemp_plotlist.append(pp)
#
#    def scrub_data(self):
#        good_cap_data = np.where(self.data[:, 4] > 1.2)
#        self.data = self.data[good_cap_data]
#        good_loss_data = np.where(np.logical_and(self.data[:, 5] > 0, self.data[:, 5] <= 1))
#        self.data = self.data[good_loss_data]
#
#    def start(self):
#        #proxy = pg.SignalProxy(self.C_v_time.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved_ctime)
#        self.update()
#        self.win.raise_()
#        self.timer = QtCore.QTimer()
#        self.timer.setInterval(50000)
#        self.timer.timeout.connect(self.update)
#        self.timer.start(1)
#        self.app.exec_()
#        time.sleep(1)
#        self.app.exec_()
#        #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        #    QtGui.QApplication.instance().exec_()
#
#    ## Start Qt event loop unless running in interactive mode or using pyside.
#if __name__ == '__main__':
#    import data_files
#    import os
#    import datetime
#    import sys; sys.path.append('../GPIB')
#    import get
#
#    date = str(datetime.date.today()).split('-')
#    year = int(date[0])
#    month = int(date[1])
#    day = int(date[2])
#    if len(sys.argv) == 3:
#        month = sys.argv[1]
#        day = sys.argv[2]
#    elif len(sys.argv) == 4:
#        year = sys.argv[3]
#        month = sys.argv[1]
#        day = sys.argv[2]
#    elif len(sys.argv) == 2:
#        day = sys.argv[1]
#
#    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
#    filenames = data_files.file_name(month, day, year)
#
#    plots = Plotter(path=filepath, data_file=filenames[0], plot_num=1, title="ZMF")
#    plots.update()
#    plots.start()
#
#