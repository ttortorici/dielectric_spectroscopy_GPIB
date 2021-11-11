import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QRunnable, Qt, QThread, QObject, pyqtSignal
import PyQt5.QtGui as qtg
from start_meas_dialog import StartMeasDialog
import threading
from _thread import *
import client_tools
import socket
import time


class ControlTab(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent

        self.layout = qtw.QVBoxLayout(self)

        intro = qtw.QLabel("LakeShore Remote Control")
        intro.setAlignment(Qt.AlignCenter)
        intro.setFont(qtg.QFont('Arial', 20))
        self.layout.addWidget(intro)

        """CONTROLS"""
        labels = ['Model', 'Heater Power Range [W]', 'Ramp Speed [K/min]', 'Setpoint [K]', 'PID']

        self.modelChoice = qtw.QComboBox()
        self.modelChoice.addItems(['LS331', 'LS340'])

        self.heaterRangeChoice = qtw.QComboBox()
        self.heaterRangeChoice.addItems(['Off', '500 mW', '5 W'])

        self.rampSpeed = qtw.QSpinBox()
        self.rampSetButton = qtw.QPushButton()
        self.rampSetButton.setText('Apply')
        self.rampSetButton.setFixedWidth(100)
        # self.rampSetButton.clicked.connect(self.set_ramp_speed)

        self.setpointEntry = qtw.QSpinBox()
        self.setpointButton = qtw.QPushButton()
        self.setpointButton.setText('Apply')
        self.setpointButton.setFixedWidth(100)
        # self.setpointButton.clicked.connect(self.set_setpoint)

        self.pValue = qtw.QSpinBox()
        self.iValue = qtw.QSpinBox()
        self.dValue = qtw.QSpinBox()
        self.pidButton = qtw.QPushButton()
        self.pidButton.setText('Apply')
        self.pidButton.setFixedWidth(100)
        # self.pidButton.clicked.connect(self.set_PID)

        widgets = [[self.modelChoice],
                   [self.heaterRangeChoice],
                   [self.rampSpeed, self.rampSetButton],
                   [self.setpointEntry, self.setpointButton],
                   [self.pValue, self.iValue, self.dValue, self.pidButton]]

        grid = qtw.QGridLayout()

        for ii, label, widget in zip(range(len(labels)), labels, widgets):
            labelW = qtw.QLabel(label)
            labelW.setAlignment(Qt.AlignRight | Qt.AlignCenter)
            # labelW.setSizePolicy(qtg.QSizePolicy.Expanding, qtg.QSizePolicy.Expanding)
            labelW.setFont(qtg.QFont('Arial', 16))
            row_widget = qtw.QWidget()
            row_layout = qtw.QHBoxLayout()
            for w in widget:
                if not (isinstance(w, qtw.QComboBox) or isinstance(w, qtw.QPushButton)):
                    w.setAlignment(Qt.AlignCenter)
                w.setFont(qtg.QFont('Arial', 16))
                row_layout.addWidget(w)
            row_widget.setLayout(row_layout)
            grid.addWidget(labelW, ii, 0)
            grid.addWidget(row_widget, ii, 1)
        self.layout.addLayout(grid)

        """UPDATED VALUES"""

        live_rowW = qtw.QWidget()
        live_rowL = qtw.QHBoxLayout()

        labels = ['Temperature', 'Heater Output', 'Setpoint', 'Ramp Status']
        colors = ['lightblue', 'pink', 'lightgrey', 'lightgreen']
        widths = [120, 110, 120, 50]

        self.tempValue = qtw.QLineEdit()
        self.heaterValue = qtw.QLineEdit()
        self.setpointValue = qtw.QLineEdit()
        self.rampStatus = qtw.QLineEdit()

        widgets = [self.tempValue, self.heaterValue, self.setpointValue, self.rampStatus]

        for label, widget, color, width in zip(labels, widgets, colors, widths):
            labelW = qtw.QLabel(label)
            labelW.setFont(qtg.QFont('Arial', 16))
            widget.setReadOnly(True)
            widget.setFont(qtg.QFont('Arial', 16))
            widget.setStyleSheet("QLineEdit{background : %s;}" % color)
            widget.setAlignment(Qt.AlignRight)
            widget.setFixedWidth(width)
            live_rowL.addWidget(labelW)
            live_rowL.addWidget(widget)
        live_rowW.setLayout(live_rowL)
        self.layout.addWidget(live_rowW)
        self.setLayout(self.layout)

    def update_values(self, temperature, heater, setpoint, ramp):
        print(temperature)
        self.tempValue.setText('%.2f K' % temperature)
        self.heaterValue.setText(f'{heater} %')
        self.setpointValue.setText('%.2f K' % setpoint)
        self.rampStatus.setText('On' if ramp else 'Off')
