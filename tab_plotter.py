import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from start_meas_dialog import StartMeasDialog
import numpy as np
import os
import sys
import time
import pyqtgraph as pg
import numpy as np
import Plotting_scripts.DateAxisItem as DateAxisItem
import Plotting_scripts.plotting_tools as tools


pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class PlotterTab(qtw.QWidget):
    colorsC = [(155, 0, 0),         # dark red
               (76, 145, 0),        # dark green
               (0, 0, 200),         # dark blue
               (122, 23, 220),      # purple
               (204, 102, 0)]       # dark orange]
    colorsL = [(255, 101, 102),     # rose
               (51, 255, 153),      # light green
               (0, 204, 204),       # cyan
               (228, 104, 232),     # magenta
               (255, 152, 51)]      # orange
    colors2 = [(255, 0, 0), (0, 0, 255)]

    def __init__(self, parent, base_path):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent
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

        "Place Plots in the window"
        self.layout.addWidget(self.plot_CvT, 0, 0)
        self.layout.addWidget(self.plot_LvT, 1, 0)
        self.layout.addWidget(self.plot_Tvt, 0, 1)
        self.layout.addWidget(self.plot_Cvt, 1, 1)
        self.setLayout(self.layout)

        """These will be the curves drawn on the plots"""
        self.c_curves = [None]      # these will be the curves drawn for capacitance vs temperature
        self.l_curves = [None]      # these will be the curves drawn for loss tangent vs temperature
        self.ct_curves = [None]     # these will be the curves drawn for capacitance vs time
        self.lt_curves = [None]     # these will be the curves drawn for loss tangent vs time
        self.T_curves = [None]      # these will be the curves drawn for Temperature vs time

        """Where to find the columns in the data"""
        self.time_indexes = None
        self.tempA_indexes = None
        self.tempB_indexes = None
        self.cap_indexes = None
        self.loss_indexes = None

        """These will be pen objects for drawing the curves on the plots"""
        self.pensC = [None]
        self.pensL = [None]
        self.pens2 = [None]

    def initialize_plotter(self, filename):
        self.filename = filename
        print(self.filename)

        freq_num = len(self.parent.tabMeas.dialog.freq_entry)

        self.c_curves *= freq_num
        self.l_curves *= freq_num
        self.ct_curves *= freq_num * 2
        self.lt_curves *= freq_num

        self.pensC *= freq_num
        self.pensL *= freq_num
        self.pens2 *= len(PlotterTab.colors2)

        for ii, color in enumerate(PlotterTab.colorsC[:freq_num]):
            self.pensC[ii] = pg.mkPen(color, width=2)
        for ii, color in enumerate(PlotterTab.colorsL[:freq_num]):
            self.pensL[ii] = pg.mkPen(color, width=2)
        for ii, color in enumerate(PlotterTab.colors2):
            self.pens2[ii] = pg.mkPen(color, width=2)

        """Find labels from the data file"""
        labels = tools.get_labels(self.filename)

        flabels = [''] * len(self.filename)
        for ii, f in enumerate(self.filename):
            flabels[ii] = tools.get_f_labels(self.filename, labels)

        flabels = tools.most_common(flabels)
        for ii, label in enumerate(flabels):
            offset = len(flabels)
            self.c_curves[ii] = self.plot_CvT.plot(pen=self.pensC[ii], name=label)
            self.l_curves[ii] = self.plot_LvT.plot(pen=self.pensL[ii], name=label)
            self.ct_curves[ii] = self.plot_Cvt.plot(pen=self.pensC[ii], name=label + ' capacitance')
            self.ct_curves[ii+offset] = self.plot_Cvt.plot(pen=self.pensL[ii], name=label + ' loss')
            self.lt_curves[ii] = pg.PlotCurveItem(pen=self.pensL[ii], name=label)
            self.plot_Lvt.addItem(self.lt_curves[ii])

        stage_num = 1
        T_labels = ['Sample Stage']
        for l in labels:
            if 'temperature b' in l.lower():
                stage_num += 1
                T_labels.append('Cooling Stage')
                self.plot_Tvt.addLegend()
                break
        self.T_curves *= stage_num

        for ii, l in enumerate(T_labels):
            self.T_curves[ii] = self.plot_Tvt.plot(pen=self.pens2[ii], name=l)

        self.time_indexes = [ii for ii, ll in enumerate(labels) if 'time' in ll.lower()]
        if len(T_labels) == 1:
            self.tempA_indexes = [ii for ii, ll in enumerate(labels) if 'temperature' in ll.lower()]
            self.tempB_indexes = None
        else:
            self.tempA_indexes = [ii for ii, ll in enumerate(labels) if 'temperature a' in ll.lower()]
            self.tempB_indexes = [ii for ii, ll in enumerate(labels) if 'temperature b' in ll.lower()]
        self.cap_indexes = [ii for ii, ll in enumerate(labels) if 'capacitance' in ll.lower()]
        self.loss_indexes = [ii for ii, ll in enumerate(labels) if 'loss' in ll.lower()]

        self.updateViews()
        self.plot_Cvt.getViewBox().sigResized.connect(self.updateViews)

        self.plot_Tvt.setXRange(time.time(), time.time() + 360, padding=0)
        print('done')

    def updateViews(self):
        self.plot_Lvt.setGeometry(self.plot_Cvt.getViewBox().sceneBoundingRect())
        self.plot_Lvt.linkedViewChanged(self.plot_Cvt.getViewBox(), self.plot_Lvt.XAxis)

    def updatePlots(self):
        print('UDPATING PLOT')
        data = tools.load_data(self.filename)
        print(data)

        print(self.time_indexes)
        print(self.cap_indexes)
        print(self.loss_indexes)
        print(self.tempA_indexes)

        ts = [data[:, ind] for ind in self.time_indexes]
        Ts = [data[:, ind] for ind in self.tempA_indexes]
        if self.tempB_indexes:
            TBs = [data[:, ind] for ind in self.tempB_indexes]
        else:
            TBs = None
        Cs = [data[:, ind] for ind in self.cap_indexes]
        Ls = [data[:, ind] for ind in self.loss_indexes]

        print(ts)
        for curve, t, C in zip(self.ct_curves, ts, Cs):
            curve.setData(x=t, y=C)
        for curve, t, L in zip(self.lt_curves, ts, Ls):
            curve.setData(x=t, y=L)
        for curve, T, C in zip(self.c_curves, Ts, Cs):
            curve.setData(x=T, y=C)
        for curve, T, L in zip(self.l_curves, Ts, Ls):
            curve.setData(x=T, y=L)
        if TBs:
            data = np.column_stack((np.concatenate(ts),
                                    np.concatenate(Ts),
                                    np.concatenate(TBs)))
        else:
            data = np.column_stack((np.concatenate(ts),
                                    np.concatenate(Ts)))
        data = np.array(sorted(data, key=lambda row: row[0]))
        for ii, curve in enumerate(self.T_curves):
            curve.setData(x=data[:, 0], y=data[:, ii+1])

