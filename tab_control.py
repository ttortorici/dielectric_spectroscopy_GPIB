import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal
import PyQt5.QtGui as qtg
import threading


"""class ButtonHandler(qtw.QWidget):

    send_b = pyqtSignal(bool)
    send_ls = pyqtSignal(bool)
    ave = pyqtSignal(bool)
    heater = pyqtSignal(bool)
    ramp = pyqtSignal(bool)
    setpt = pyqtSignal(bool)
    pid = pyqtSignal(bool)

    def activate(self, label):
        label = label.lower()
        if 'ave' in label:
            self.ave.emit(True)
        elif 'heat' in label:
            self.heater.emit(True)
        elif 'ramp' in label:
            self.ramp.emit(True)
        elif 'set' in label:
            self.setpt.emit(True)
        elif 'pid' in label:
            self.pid.emit(True)
        elif 'send' in label:
            if 'ls' in label:
                self.send_ls.emit(True)
            else:
                self.send_b.emit(True)
        elif 'reset' in label:
            if 'ls' in label:
                self.reset_ls.emit(True)

    def deactivate(self, label):
        label = label.lower()
        if 'ave' in label:
            self.ave.emit(False)
        elif 'heat' in label:
            self.heater.emit(False)
        elif 'ramp' in label:
            self.ramp.emit(False)
        elif 'set' in label:
            self.setpt.emit(False)
        elif 'pid' in label:
            self.pid.emit(False)
        elif 'send' in label:
            if 'ls' in label:
                self.send_ls.emit(False)
            else:
                self.send_b.emit(False)"""


class ButtonHandler(qtw.QWidget):

    active = pyqtSignal(bool)

    def activate(self):
        self.active.emit(True)

    def deactivate(self):
        self.active.emit(False)


class ControlTab(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent

        self.ls = None  # lakeshore class will pull from measure tabs .data class
        self.button_handler = ButtonHandler()
        self.button_handler.active.connect(self.buttons_active)
        # self.button_handler.ave.connect(self.averaging_button_active)
        # self.button_handler.heater.connect(self.heater_button_active)
        # self.button_handler.ramp.connect(self.ramp_button_active)
        # self.button_handler.setpt.connect(self.setpt_button_active)
        # self.button_handler.pid.connect(self.pid_button_active)
        # self.button_handler.send_b.connect(self.send_bridge_button_active)
        # self.button_handler.send_ls.connect(self.send_ls_button_active)

        self.layout = qtw.QVBoxLayout(self)

        bridge_intro = qtw.QLabel("Bridge Remote Control")
        bridge_intro.setAlignment(Qt.AlignCenter)
        bridge_intro.setFont(qtg.QFont('Arial', 20))
        self.layout.addWidget(bridge_intro)

        labels = ['Averaging', 'Send Message']

        self.averagingTime = qtw.QSpinBox()
        self.averagingTime.setMaximum(15)
        self.averagingButton = qtw.QPushButton()
        self.averagingButton.setText('Apply')
        self.averagingButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.averagingButton.setFixedWidth(100)
        self.averagingButton.clicked.connect(self.set_averaging)
        self.aveUpdateButton = qtw.QPushButton()
        self.aveUpdateButton.setText('Refresh')
        self.aveUpdateButton.setFixedWidth(100)
        self.aveUpdateButton.clicked.connect(self.update_averaging)

        self.sendBridge = qtw.QLineEdit()
        self.sendBridgeButton = qtw.QPushButton()
        self.sendBridgeButton.setText('Send')
        self.sendBridgeButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.sendBridgeButton.setFixedWidth(100)
        self.sendBridgeButton.clicked.connect(self.send_bridge)
        self.sendBridgeReset = qtw.QPushButton()
        self.sendBridgeReset.setText('Reset')
        self.sendBridgeReset.setFixedWidth(100)
        self.sendBridgeReset.clicked.connect(self.send_bridge_reset)

        widgets = [[self.averagingTime, self.averagingButton, self.aveUpdateButton],
                   [self.sendBridge, self.sendBridgeButton, self.sendBridgeReset]]

        self.buttons = [self.averagingButton, self.aveUpdateButton, self.sendBridgeButton, self.sendBridgeReset]

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


        ls_intro = qtw.QLabel("LakeShore Remote Control")
        ls_intro.setAlignment(Qt.AlignCenter)
        ls_intro.setFont(qtg.QFont('Arial', 20))
        self.layout.addWidget(ls_intro)

        """CONTROLS"""
        labels = ['Model', 'Heater Power Range [W]', 'Ramp Speed [K/min]', 'Setpoint [K]', 'PID', 'Send Message']

        self.modelChoice = qtw.QComboBox()
        self.model_choices = ['LS331', 'LS340']
        self.modelChoice.addItems(self.model_choices)

        self.heaterRangeChoice = qtw.QComboBox()
        self.heater_range_choices = ['Off', '500 mW', '5 W']
        self.heaterRangeChoice.addItems(self.heater_range_choices)
        self.heaterRangeChoice.activated.connect(self.set_heater_range)
        self.heaterRangeUpdateButton = qtw.QPushButton()
        self.heaterRangeUpdateButton.setText('Refresh')
        self.heaterRangeUpdateButton.setFixedWidth(100)
        self.heaterRangeUpdateButton.clicked.connect(self.update_heater_range)

        self.rampSpeed = qtw.QDoubleSpinBox()
        self.rampSpeed.setDecimals(1)
        self.rampSpeed.setMaximum(100.0)
        self.rampSetButton = qtw.QPushButton()
        self.rampSetButton.setText('Apply')
        self.rampSetButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.rampSetButton.setFixedWidth(100)
        self.rampSetButton.clicked.connect(self.set_ramp_speed)
        self.rampUpdateButton = qtw.QPushButton()
        self.rampUpdateButton.setText('Refresh')
        self.rampUpdateButton.setFixedWidth(100)
        self.rampUpdateButton.clicked.connect(self.update_ramp_speed)

        self.setpointEntry = qtw.QDoubleSpinBox()
        self.setpointEntry.setDecimals(2)
        self.setpointEntry.setMaximum(400.00)
        self.setpointButton = qtw.QPushButton()
        self.setpointButton.setText('Apply')
        self.setpointButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.setpointButton.setFixedWidth(100)
        self.setpointButton.clicked.connect(self.set_setpoint)
        self.setptUpdateBotton = qtw.QPushButton()
        self.setptUpdateBotton.setText('Refresh')
        self.setptUpdateBotton.setFixedWidth(100)
        self.setptUpdateBotton.clicked.connect(self.update_setpoint)

        self.pValue = qtw.QDoubleSpinBox()
        self.iValue = qtw.QDoubleSpinBox()
        self.dValue = qtw.QDoubleSpinBox()
        self.pValue.setDecimals(1)
        self.iValue.setDecimals(1)
        self.dValue.setDecimals(1)
        self.pValue.setMaximum(1000.0)
        self.iValue.setMaximum(1000.0)
        self.dValue.setMaximum(1000.0)
        self.pidButton = qtw.QPushButton()
        self.pidButton.setText('Apply')
        self.pidButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.pidButton.setFixedWidth(100)
        self.pidButton.clicked.connect(self.set_PID)
        self.pidUpdateButton = qtw.QPushButton()
        self.pidUpdateButton.setText('Refresh')
        self.pidUpdateButton.setFixedWidth(100)
        self.pidUpdateButton.clicked.connect(self.update_PID)

        self.sendLs = qtw.QLineEdit()
        self.sendLsButton = qtw.QPushButton()
        self.sendLsButton.setText('Send')
        self.sendLsButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.sendLsButton.setFixedWidth(100)
        self.sendLsButton.clicked.connect(self.send_ls)
        self.sendLsReset = qtw.QPushButton()
        self.sendLsReset.setText('Reset')
        self.sendLsReset.setFixedWidth(100)
        self.sendLsReset.clicked.connect(self.send_ls_reset)

        widgets = [[self.modelChoice],
                   [self.heaterRangeChoice, self.heaterRangeUpdateButton],
                   [self.rampSpeed, self.rampSetButton, self.rampUpdateButton],
                   [self.setpointEntry, self.setpointButton, self.setptUpdateBotton],
                   [self.pValue, self.iValue, self.dValue, self.pidButton, self.pidUpdateButton],
                   [self.sendLs, self.sendLsButton, self.sendLsReset]]

        self.buttons += [self.heaterRangeUpdateButton, self.rampSetButton, self.rampUpdateButton,
                         self.setpointButton, self.setptUpdateBotton, self.pidButton, self.pidUpdateButton,
                         self.sendLsButton, self.sendLsReset]

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
            # live_rowL.addWidget(labelW)
            live_rowL.addWidget(widget)
            live_rowL.addWidget(labelW)
        live_rowW.setLayout(live_rowL)
        self.layout.addWidget(live_rowW)
        self.setLayout(self.layout)

    @pyqtSlot(float, float, float, bool)
    def update_values(self, temperature, heater, setpoint, ramp):
        print(temperature)
        self.tempValue.setText('%.2f K' % temperature)
        self.heaterValue.setText(f'{heater} %')
        self.setpointValue.setText('%.2f K' % setpoint)
        self.rampStatus.setText('On' if ramp else 'Off')

    @pyqtSlot()
    def initialize(self):
        print('\n\n initialize received \n\n')
        self.ls = self.parent.tabMeas.data.ls
        self.bridge = self.parent.tabMeas.data.bridge

        self.averagingTime.setValue(self.bridge.read_ave())

        self.modelChoice.setCurrentIndex(self.model_choices.index(f'LS{self.ls.inst_num}'))
        hrange = self.ls.read_heater_range()
        if hrange > 1:
            hstring = f'{int(hrange)} W'
        elif not hrange:
            hstring = 'Off'
        else:
            hstring = f'{int(hrange*1000)} mW'
        self.heaterRangeChoice.setCurrentIndex(self.heater_range_choices.index(hstring))
        self.rampSpeed.setValue(self.ls.read_ramp_speed())
        self.setpointEntry.setValue(self.ls.read_setpoint())
        pid = self.ls.read_PID()
        self.pValue.setValue(pid[0])
        self.iValue.setValue(pid[1])
        self.dValue.setValue(pid[2])

    @pyqtSlot()
    def send_bridge(self):
        t = threading.Thread(target=self.send_bridge_thread, args=())
        t.start()

    def send_bridge_thread(self):
        self.button_handler.deactivate()
        msg_out = self.sendBridge.text()
        if msg_out:
            msg_back = self.bridge.query(str(msg_out))
            self.sendBridge.setText(str(msg_back))
        self.button_handler.activate()

    @pyqtSlot()
    def send_bridge_reset(self):
        self.sendBridge.setText('')

    @pyqtSlot()
    def send_ls(self):
        t = threading.Thread(target=self.send_ls_thread, args=())
        t.start()

    def send_ls_thread(self):
        self.button_handler.deactivate()
        msg_out = self.sendLs.text()
        if msg_out:
            msg_back = self.ls.query(str(msg_out))
            self.sendLs.setText(str(msg_back))
        self.button_handler.activate()

    @pyqtSlot()
    def send_ls_reset(self):
        self.sendLs.setText('')

    @pyqtSlot()
    def set_averaging(self):
        t = threading.Thread(target=self.set_averaging_thread, args=())
        t.start()

    def set_averaging_thread(self):
        print('Setting Averaging')
        self.button_handler.deactivate()
        self.bridge.set_ave(float(self.averagingTime.text()))
        self.button_handler.activate()

    @pyqtSlot()
    def update_averaging(self):
        self.button_handler.deactivate()
        self.averagingTime.setValue(self.bridge.read_ave())
        self.button_handler.activate()

    @pyqtSlot()
    def set_heater_range(self):
        t = threading.Thread(target=self.set_heater_range_thread, args=())
        t.start()

    def set_heater_range_thread(self):
        print('Setting heater')
        self.button_handler.deactivate()
        hstring = self.heaterRangeChoice.currentText()
        if hstring == 'Off':
            hrange = 0.
        elif 'mW' in hstring:
            hrange = float(hstring.strip('mW')) / 1000.
        else:
            hrange = float(hstring.strip('W'))
        self.ls.set_heater_range(hrange)
        print('Set heater')
        self.button_handler.activate()

    @pyqtSlot()
    def update_heater_range(self):
        self.button_handler.deactivate()
        hrange = self.ls.read_heater_range()
        if hrange > 1:
            hstring = f'{int(hrange)} W'
        elif not hrange:
            hstring = 'Off'
        else:
            hstring = f'{int(hrange * 1000)} mW'
        self.heaterRangeChoice.setCurrentIndex(self.heater_range_choices.index(hstring))
        self.button_handler.activate()

    @pyqtSlot()
    def set_ramp_speed(self):
        t = threading.Thread(target=self.set_ramp_speed_thread, args=())
        t.start()

    def set_ramp_speed_thread(self):
        self.button_handler.deactivate()
        self.ls.set_ramp_speed(float(self.rampSpeed.text()))
        self.button_handler.activate()

    @pyqtSlot()
    def update_ramp_speed(self):
        self.button_handler.deactivate()
        self.rampSpeed.setValue(self.ls.read_ramp_speed())
        self.button_handler.activate()

    @pyqtSlot()
    def set_setpoint(self):
        t = threading.Thread(target=self.set_setpoint_thread, args=())
        t.start()

    def set_setpoint_thread(self):
        self.button_handler.deactivate()
        self.ls.set_setpoint(float(self.setpointEntry.text()))
        self.button_handler.activate()

    @pyqtSlot()
    def update_setpoint(self):
        self.button_handler.deactivate()
        self.setpointEntry.setValue(self.ls.read_setpoint())
        self.button_handler.activate()

    @pyqtSlot()
    def set_PID(self):
        t = threading.Thread(target=self.set_PID_thread, args=())
        t.start()

    def set_PID_thread(self):
        self.button_handler.deactivate()
        P = float(self.pValue.text())
        I = float(self.iValue.text())
        D = float(self.dValue.text())
        self.ls.set_PID(P, I, D)
        self.button_handler.activate()

    @pyqtSlot()
    def update_PID(self):
        self.button_handler.deactivate()
        pid = self.ls.read_PID()
        self.pValue.setValue(pid[0])
        self.iValue.setValue(pid[1])
        self.dValue.setValue(pid[2])
        self.button_handler.activate()

    @pyqtSlot(bool)
    def buttons_active(self, activate):
        for button in self.buttons:
            button.setEnabled(activate)

    """@pyqtSlot(bool)
    def averaging_button_active(self, activate):
        self.averagingButton.setEnabled(activate)
        self.aveUpdateButton.setEnabled(activate)

    @pyqtSlot(bool)
    def heater_button_active(self, activate):
        self.heaterRangeChoice.setEnabled(activate)

    @pyqtSlot(bool)
    def ramp_button_active(self, activate):
        self.rampSetButton.setEnabled(activate)

    @pyqtSlot(bool)
    def setpt_button_active(self, activate):
        self.setpointButton.setEnabled(activate)

    @pyqtSlot(bool)
    def pid_button_active(self, activate):
        self.pidButton.setEnabled(activate)

    @pyqtSlot(bool)
    def send_bridge_button_active(self, activate):
        self.sendBridgeButton.setEnabled(activate)

    @pyqtSlot(bool)
    def send_ls_button_active(self, activate):
        self.sendLsButton.setEnabled(activate)"""
