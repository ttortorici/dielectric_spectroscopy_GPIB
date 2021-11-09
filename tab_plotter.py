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


class PlotterTab(qtw.QWidget):
    def __init__(self, parent, base_path):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.base_path = base_path

        self.layout = qtw.QVBoxLayout(self)

        self.window = pg.PlotWidget()

        self.layout.addWidget(self.window)
        self.setLayout(self.layout)

        self.curve = self.window.plot(pen='b', name='capacitance')
        self.curve.setData(x=np.arange(10), y=np.arange(10))

    def updatePlots(self):
        pass

