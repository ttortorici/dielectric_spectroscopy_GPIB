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

class Plotter:
    def __init__(self, path, data_file, title='', plot_size=(1920, 1080)):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.path = path
        self.data_file = data_file
        print os.path.join(path, data_file[0])
        data = np.loadtxt(os.path.join(path, data_file[0]), comments='#', delimiter=',', skiprows=3)
        if len(data_file) > 1:
            for ii, f in enumerate(data_file[1:]):
                data_temp = np.loadtxt(os.path.join(path, f), comments='#', delimiter=',', skiprows=3)
                try:
                    data = np.append(data, data_temp, axis=0)
                except ValueError:
                    data = np.append(data, np.array([data_temp]), axis=0)
        self.data = data
        #self.scrub_data()
        # QtGui.QApplication.setGraphicsSystem('raster')
        self.app = QtGui.QApplication([])
        # mw = QtGui.QMainWindow()
        # mw.resize(800,800)
        self.win = pg.GraphicsWindow(title=title)
        self.win.resize(plot_size[0], plot_size[1])
        self.win.setWindowFilePath(title)
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.get_frequency_locations()
        self.plot_list = []
        self.label = pg.LabelItem(justify='right')
        #self.win.addItem(self.label)
        #self.label.setText('Hi')
        #self.vLine = pg.InfiniteLine(angle=90, movable=False)

        self.colors = [(0, 0, 0),           # black
                       (255, 0, 0),         # red
                       (0, 0, 255),         # blue
                       (0, 150, 0),         # dark green
                       (255, 190, 0),       # orange
                       (200, 0, 125)]      # light red

        # set up Capacitance vs Time
        self.ax1 = DateAxisItem.DateAxisItem('bottom')
        self.C_v_time = self.win.addPlot(title="Capacitance vs Time", axisItems={'bottom': self.ax1}, row=0, col=0)
        self.C_v_time.setLabels(left='Capacitance [pF]')
        self.C_v_time.setLabels(bottom='Time')
        # create label on right axes for temperature
        self.Temp_v_time1 = pg.ViewBox()
        self.C_v_time.showAxis('right')
        self.C_v_time.scene().addItem(self.Temp_v_time1)
        self.C_v_time.getAxis('right').linkToView(self.Temp_v_time1)
        self.Temp_v_time1.setXLink(self.C_v_time)
        self.C_v_time.getAxis('right').setLabel('Temperature [K]', color='#0000ff')     # blue
        self.C_v_time.addLegend()

        # set up Capacitance vs Temperature
        self.C_v_Temp = self.win.addPlot(title="Capacitance vs Temperature", row=0, col=1)
        self.C_v_Temp.setLabels(left='Capacitance [pF]')
        self.C_v_Temp.setLabels(bottom='Temperature [K]')
        self.C_v_Temp.addLegend()

        #self.win.nextRow()      # start new row of graphs

        # set up Loss vs Time
        self.ax2 = DateAxisItem.DateAxisItem('bottom')
        self.L_v_time = self.win.addPlot(title="Loss vs Time", axisItems={'bottom': self.ax2}, row=1, col=0)
        self.L_v_time.setLabels(left='Loss tangent')
        self.L_v_time.setLabels(bottom='Time')
        # create label on right axes for temperature
        self.Temp_v_time2 = pg.ViewBox()
        self.L_v_time.showAxis('right')
        self.L_v_time.scene().addItem(self.Temp_v_time2)
        self.L_v_time.getAxis('right').linkToView(self.Temp_v_time2)
        self.Temp_v_time2.setXLink(self.L_v_time)
        self.L_v_time.getAxis('right').setLabel('Temperature [K]', color='#0000ff')     # blue
        #self.L_v_time.addLegend()

        # set up Loss vs Temp
        self.L_v_Temp = self.win.addPlot(title="Loss vs Temperature", row=1, col=1)
        self.L_v_Temp.setLabels(left='Loss Tangent')
        self.L_v_Temp.setLabels(bottom='Temperature [K]')
        self.L_v_Temp.addLegend()
        self.plot_C_v_time(init=True)
        self.plot_C_v_Temp(init=True)
        self.plot_L_v_time(init=True)
        self.plot_L_v_Temp(init=True)

    def update(self):
        data = np.loadtxt(os.path.join(self.path, self.data_file[0]), comments='#', delimiter=',', skiprows=3)
        if len(self.data_file) > 1:
            for ii, f in enumerate(self.data_file[1:]):
                data_temp = np.loadtxt(os.path.join(self.path, f), comments='#', delimiter=',', skiprows=3)
                try:
                    data = np.append(data, data_temp, axis=0)
                except ValueError:
                    data = np.append(data, np.array([data_temp]), axis=0)
        self.data = data
        self.get_frequency_locations()
        # print np.shape(self.data)
        # print np.shape(self.freq_locs['100'])
        # self.scrub_data()
        self.updateViews()
        self.plot_C_v_time()
        self.plot_C_v_Temp()
        self.plot_L_v_time()
        self.plot_L_v_Temp()

    def updateViews(self):
        """Handle view resizing"""
        # view has resized; update auxiliary views to match
        self.Temp_v_time1.setGeometry(self.C_v_time.vb.sceneBoundingRect())
        self.Temp_v_time2.setGeometry(self.L_v_time.vb.sceneBoundingRect())
        """need to re-update linked axes since this was called
           incorrectly while views had different shapes.
           (probably this should be handled in ViewBox.resizeEvent)"""
        self.Temp_v_time1.linkedViewChanged(self.C_v_time.vb, self.Temp_v_time1.XAxis)
        self.Temp_v_time2.linkedViewChanged(self.L_v_time.vb, self.Temp_v_time2.XAxis)

    def get_frequency_locations(self):
        self.frequencies = np.sort(np.unique(self.data[:, 3]))
        # print self.frequencies
        # print self.frequencies[2]
        # for freq in self.frequencies:
        #     print freq
        self.freq_locs = {}
        for freq in self.frequencies:
            self.freq_locs[str(freq)] = np.where(self.data[:, 3] == freq)

    def plot_C_v_time(self, init=False):
        if init == True:
            p1 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
                                                            pen=(0, 255, 0)))        # green
            p2 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
                                                            pen=(0, 180, 255)))  # cyan
            self.C_v_time.plot([self.data[0, 0]], [self.data[0, 4]], pen=(0, 255, 0), name="Stage Temperature")
            self.C_v_time.plot([self.data[0, 0]], [self.data[0, 4]], pen=(0, 180, 255),
                               name="Transfer Stage Temperature")
        else:
            p1 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
                                                            pen=(0, 255, 0), name="Stage Temperature"))  # cyan
            p2 = self.Temp_v_time1.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
                                                            pen=(0, 180, 255), name="Transfer Temperature"))  # cyan
        self.temp_plotlist1 = [p1, p2]
        if init == True:
            self.Ctime_plotlist = []
            for ii, freq in enumerate(self.frequencies):
                pp = self.C_v_time.plot(self.data[:, 0][self.freq_locs[str(freq)]],
                                        self.data[:, 4][self.freq_locs[str(freq)]],
                                        pen=self.colors[ii], name="%d Hz" % freq)
                self.Ctime_plotlist.append(pp)
        else:
            for ii, freq, pp in zip(xrange(len(self.frequencies)), self.frequencies, self.Ctime_plotlist):
                pp.setData(self.data[:, 0][self.freq_locs[str(freq)]], self.data[:, 4][self.freq_locs[str(freq)]])
                #print freq



    def plot_L_v_time(self, init=False):
        if init == True:
            p1 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
                                                            pen=(0, 255, 0)))  # green
            p2 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
                                                            pen=(0, 180, 255)))  # cyan
            self.L_v_time.plot([self.data[0, 0]], [self.data[0, 5]], pen=(0, 255, 0), name="Stage Temperature")
            self.L_v_time.plot([self.data[0, 0]], [self.data[0, 5]], pen=(0, 180, 255),
                               name="Transfer Stage Temperature")
        else:
            p1 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 1],
                                           pen=(0, 255, 0)))        # green
            p2 = self.Temp_v_time2.addItem(pg.PlotCurveItem(self.data[:, 0], self.data[:, 2],
                                           pen=(0, 180, 255)))      # cyan
        self.temp_plotlist2 = [p1, p2]
        if init == True:
            self.Ltime_plotlist = []
            for ii, freq in enumerate(self.frequencies):
                pp = self.L_v_time.plot(self.data[:, 0][self.freq_locs[str(freq)]],
                                        self.data[:, 5][self.freq_locs[str(freq)]],
                                        pen=self.colors[ii], name='%d Hz' % freq)
                self.Ltime_plotlist.append(pp)
        else:
            for ii, freq, pp in zip(xrange(len(self.frequencies)), self.frequencies, self.Ltime_plotlist):
                pp.setData(self.data[:, 0][self.freq_locs[str(freq)]], self.data[:, 5][self.freq_locs[str(freq)]])

    def plot_C_v_Temp(self, init=False):
        if init == True:
            self.Ctemp_plotlist = []
            for ii, freq in enumerate(self.frequencies):
                pp = self.C_v_Temp.plot(self.data[:, 1][self.freq_locs[str(freq)]],
                                        self.data[:, 4][self.freq_locs[str(freq)]],
                                        pen=self.colors[ii])
                self.Ctemp_plotlist.append(pp)
        else:
            for ii, freq, pp in zip(xrange(len(self.frequencies)), self.frequencies, self.Ctemp_plotlist):
                pp.setData(self.data[:, 1][self.freq_locs[str(freq)]], self.data[:, 4][self.freq_locs[str(freq)]])


    def plot_L_v_Temp(self, init=False):
        if init == True:
            self.Ltemp_plotlist = []
            for ii, freq in enumerate(self.frequencies):
                pp = self.L_v_Temp.plot(self.data[:, 1][self.freq_locs[str(freq)]],
                                        self.data[:, 5][self.freq_locs[str(freq)]],
                                        pen=self.colors[ii])
                self.Ltemp_plotlist.append(pp)
        else:
            for ii, freq, pp in zip(xrange(len(self.frequencies)), self.frequencies, self.Ltemp_plotlist):
                pp.setData(self.data[:, 1][self.freq_locs[str(freq)]], self.data[:, 5][self.freq_locs[str(freq)]])


    #def mouseMoved_ctime(self, evt):
    #    vb = self.C_v_time.vb
    #    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    #    if self.C_v_time.sceneBoundingRect().contains(pos):
    #        mousePoint = vb.mapSceneToView(pos)
    #    # index = np.where(data[:,0]==mousePoint.x())
    #    index2 = np.where(self.data[:, 0] >= mousePoint.x())
    #    # print len(index2),len(index2[0])
    #    if len(index2[0]) > 0:
    #        index = index2[0][0]
    #    else:
    #        index = -1
    #        # index = int(mousePoint.x())
    #    if index > 10 and index < len(self.data[:, 1]):
    #        # label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data[index,1], data[index,2]))
    #        freq = self.data[index, 3]
    #        if freq == 100:
    #            c100 = self.data[index, 4]
    #            for ii in xrange(1, 4):
    #                if self.data[index - ii, 3] == 10000:
    #                    c10000 = self.data[index - ii, 4]
    #                    break
    #            for jj in xrange(4, 7):
    #                if self.data[index - jj, 3] == 1000:
    #                    c1000 = self.data[index - jj, 4]
    #        elif freq == 1000:
    #            c1000 = self.data[index, 4]
    #            for ii in xrange(1, 4):
    #                if self.data[index - ii, 3] == 100:
    #                    c100 = self.data[index - ii, 4]
    #                    break
    #            for jj in xrange(4, 7):
    #                if self.data[index - jj, 3] == 10000:
    #                    c10000 = self.data[index - jj, 4]
    #        elif freq == 10000:
    #            c10000 = self.data[index, 4]
    #            for ii in xrange(1, 4):
    #                if self.data[index - ii, 3] == 1000:
    #                    c1000 = self.data[index - ii, 4]
    #                    break
    #            for jj in xrange(4, 7):
    #                if self.data[index - jj, 3] == 100:
    #                    c100 = self.data[index - jj, 4]
    #        msgout = "%s; %8.2fK; %8.2fK; %1.3fpF; %1.3fpF; %1.3fpF" % (
    #        time.ctime(mousePoint.x()), self.data[index, 1], self.data[index, 2], c100, c1000, c10000)
    #        self.label.setText(msgout)
    #        # print msgout
    #
    #        # print mousePoint.x(), data[index,0],data[index,1]
    #    self.vLine.setPos(mousePoint.x())
    #    # hLine.setPos(mousePoint.y())

    def scrub_data(self):
        good_cap_data = np.where(self.data[:, 4] > 1.2)
        self.data = self.data[good_cap_data]
        good_loss_data = np.where(np.logical_and(self.data[:, 5] > 0, self.data[:, 5] <= 1))
        self.data = self.data[good_loss_data]

    def start(self):
        #proxy = pg.SignalProxy(self.C_v_time.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved_ctime)
        self.update()
        self.win.raise_()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50000)
        self.timer.timeout.connect(self.update)
        self.timer.start(1)
        self.app.exec_()
        time.sleep(1)
        self.app.exec_()
        #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        #    QtGui.QApplication.instance().exec_()

    ## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import data_files
    import os
    import datetime
    import sys; sys.path.append('../GPIB')
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

    plots = Plotter(path=filepath, data_file=filenames[0], title="ZMF")
    plots.update()
    plots.start()

