import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from start_meas_dialog import StartMeasDialog
import numpy as np
import os
import sys
import pyqtgraph as pg
import numpy as np
import Plotting_scripts.DateAxisItem as DateAxisItem
import Plotting_scripts.plotting_tools as tools


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

        self.c_curves = ['']
        self.l_curves = ['']
        self.ct_curves = ['']
        self.lt_curves = ['']
        self.T_curves = [None]

        self.time_indexes = None
        self.tempA_indexes = None
        self.tempB_indexes = None
        self.cap_indexes = None
        self.loss_indexes = None

    def initialize_plotter(self, filename):
        self.filename = filename
        print(self.filename)

        self.c_curves *= len(self.parent.tabMeas.dialog.freq_entry)
        self.l_curves *= len(self.parent.tabMeas.dialog.freq_entry)
        self.ct_curves *= len(self.parent.tabMeas.dialog.freq_entry) * 2
        self.lt_curves *= len(self.parent.tabMeas.dialog.freq_entry)

        labels = tools.get_labels(self.filename)
        # print(labels)

        flabels = [''] * len(self.filename)
        for ii, f in enumerate(self.filename):
            flabels[ii] = tools.get_f_labels(self.filename, labels)
            # print(flabels)

        flabels = tools.most_common(flabels)
        for ii, label in enumerate(flabels):
            offset = len(flabels)
            self.c_curves[ii] = self.plot_CvT.plot(pen=self.pens6[ii], name=label)
            self.l_curves[ii] = self.plot_LvT.plot(pen=self.pens6[ii+offset], name=label)
            self.ct_curves[ii] = self.plot_Cvt.plot(pen=self.pens6[ii], name=label+' capacitance')
            self.ct_curves[ii+offset] = self.plot_Cvt.plot(pen=self.pens6[ii+offset], name=label+' loss')
            self.lt_curves[ii] = pg.PlotCurveItem(pen=self.pens6[ii+offset], name=label)
            self.plot_Lvt.addItem(self.lt_curves[ii])

        stage_num = 1
        T_labels = ['Sample Stage']
        for l in labels:
            if 'temperature b' in l.lower():
                stage_num += 1
                T_labels.append('Cooling Stage')
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
        # print(self.time_indexes)
        # print(self.tempA_indexes)
        # print(self.cap_indexes)
        # print(self.loss_indexes)
        self.updateViews()
        self.plot_Cvt.getViewBox().sigResized.connect(self.updateViews)

    def updateViews(self):
        self.plot_Lvt.setGeometry(self.plot_Cvt.getViewBox().sceneBoundingRect())
        self.plot_Lvt.linkedViewChanged(self.plot_Cvt.getViewBox(), self.plot_Lvt.XAxis)

    def updatePlots(self):
        data = tools.load_data(self.filename)

        ts = [data[:, ind] for ind in self.time_indexes]
        Ts = [data[:, ind] for ind in self.tempA_indexes]
        if self.tempB_indexes:
            TBs = [data[:, ind] for ind in self.tempB_indexes]
        else:
            TBs = None
        Cs = [data[:, ind] for ind in self.cap_indexes]
        Ls = [data[:, ind] for ind in self.loss_indexes]

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

