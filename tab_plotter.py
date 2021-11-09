import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from start_meas_dialog import StartMeasDialog
import socket
import numpy as np
import os
import sys
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
import Plotting_scripts.DateAxisItem as DateAxisItem
import itertools
import csv
import operator

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class PlotterTab(qtw.QWidget):
    colors6 = [(204, 0, 0),     # dark red
               (76, 153, 0),    # dark green
               (0, 0, 204),     # dark blue
               (255, 128, 0),   # orange
               (0, 204, 204),   # cyan
               (153, 51, 255)]  # purple
    colors2 = [(255, 0, 0), (0, 0, 255)]

    def __init__(self, parent, base_path):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.base_path = base_path
        self.filename = None

        self.layout = qtw.QGridLayout(self)

        self.plot_CvT = pg.PlotWidget()
        self.plot_CvT.setLabel('left', 'Capacitance (pF)')
        self.plot_CvT.setLabel('bottom', 'Temperature (K)')
        self.plot_CvT.addLegend()

        self.plot_LvT = pg.PlotWidget()
        self.plot_LvT.setLabel('left', 'Loss Tangent')
        self.plot_LvT.setLabel('bottom', 'Temperature (K)')
        self.plot_LvT.addLegend()
        self.plot_LvT.setXLink(self.plot_CvT)

        self.plot_Tvt = pg.PlotWidget()
        self.plot_Tvt.setLabel('left', 'Temperature (K)')
        self.plot_Tvt.setLabel('bottom', 'time')
        self.plot_Tvt.setAxisItems({'bottom': DateAxisItem.DateAxisItem('bottom')})

        self.plot_Cvt = pg.PlotWidget()
        self.plot_Cvt.setLabel('left', 'Temperature (K)')
        self.plot_Cvt.setLabel('right', 'Loss Tangent')
        self.plot_Cvt.setLabel('bottom', 'time')
        self.plot_Cvt.setAxisItems({'bottom': DateAxisItem.DateAxisItem('bottom')})
        self.plot_Cvt.setXLink(self.plot_Tvt)

        self.plot_Lvt = pg.ViewBox()
        self.plot_Cvt.scene().addItem(self.plot_Lvt)
        self.plot_Cvt.getAxis('right').linkToView(self.plot_Lvt)
        self.plot_Lvt.setXLink(self.plot_Cvt)
        self.plot_Tvt.setXLink(self.plot_Cvt)

        self.layout.addWidget(self.plot_CvT, 0, 0)
        self.layout.addWidget(self.plot_LvT, 1, 0)
        self.layout.addWidget(self.plot_Tvt, 0, 1)
        self.layout.addWidget(self.plot_Cvt, 1, 1)
        self.setLayout(self.layout)

        self.pens6 = [''] * len(PlotterTab.colors6)
        self.pens2 = [''] * len(PlotterTab.colors2)
        for ii, color in enumerate(PlotterTab.colors6):
            self.pens6[ii] = pg.mkPen(color, width=2)
        for ii, color in enumerate(PlotterTab.colors2):
            self.pens2[ii] = pg.mkPen(color, width=2)

        self.curve = self.plot_Cvt.plot(pen='b', name='capacitance')
        self.curve.setData(x=np.arange(10), y=np.arange(10))

    def updateFile(self, filename):
        self.filename = filename

    def updatePlots(self):
        pass

