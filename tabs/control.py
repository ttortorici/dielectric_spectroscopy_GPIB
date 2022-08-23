"""
A tab widget for controlling devices in app.py

@author: Teddy Tortorici
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QSpinBox, QPushButton, QLineEdit, QGridLayout, QHBoxLayout,
                               QComboBox, QLabel, QDoubleSpinBox, QMainWindow)
from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QFont
import threading


label_font = QFont("Arial", 16)


class ButtonHandler(QWidget):
    """Allows you to turn buttons on or off from a signal"""
    activate = Signal(bool)


class ControlTab(QWidget):

    title_font = QFont("Arial", 20)

    def __init__(self, parent: QMainWindow):
        QWidget.__init__(self)
        self.parent = parent

        self.button_activator = ButtonHandler()
        self.button_activator.activate.connect(self.buttons_enabled)

        main_layout = QVBoxLayout()

        """DEVICE CONTROLLER: LakeShore"""
        # Title
        self.ls = None  # will get from self.parent.data_tab once a server is running
        ls_intro = self.Title("Lakeshore Remote Control")

        main_layout.addWidget(ls_intro)

        # Controls
        labels = ["Heater Power Range [W]", "Ramp Speed [K/min]", "Setpoint [K]", "PID", "Send Command"]

        self.heater_range_row = HeaterRangeRow(self)

        main_layout.addLayout(self.heater_range_row)

        self.setLayout(main_layout)


    @Slot(bool)
    def buttons_enabled(self, on: bool):
        for button in self.buttons:
            button.setEnabled(on)

    class Title(QLabel):
        def __init__(self, text: str):
            super(self.__class__, self).__init__(text)
            self.setAlignment(Qt.AlignCenter)
            self.setFont(ControlTab.title_font)


class Label(QLabel):
    def __init__(self, text: str):
        super(self.__class__, self).__init__(text)
        self.setFont(label_font)
        self.setAlignment(Qt.AlignRight | Qt.AlignCenter)


class HeaterRangeRow(QHBoxLayout):
    def __init__(self, parent: ControlTab):
        super(self.__class__, self).__init__()
        self.parent = parent

        label = Label("Heater Power Range")
        self.box = QComboBox()
        self.box.setFont(label_font)
        self.choices = ["Off", "500 mW", "5 W"]
        self.range_values = dict(zip(self.choices, [0, 0.5, 5]))
        self.box.addItems(self.choices)
        self.box.activated.connect(self.set)

        widgets = [label, self.box]
        for widget in widgets:
            self.addWidget(widget)

    @Slot()
    def set(self):
        """To allow the process to run in the background"""
        t = threading.Thread(target=self.set_thread, args=())
        t.daemon = True         # makes it so if the main thread shuts down, you don't have to wait for this.
        t.start()

    def set_thread(self):
        """What happens when you change the selection"""
        # Turn off buttons
        self.parent.button_activator.activate.emit(False)
        print("Setting Heater")
        heater_choice = self.box.currentText()
        heater_range = self.range_values[heater_choice]
        self.parent.ls.set_heater_range(heater_range)
        print(f"Set heater to {heater_choice}")
        self.parent.button_activator.activate.emit(True)

    def update_box(self):
        """Run update in a thread"""
        t = threading.Thread(target=self.update_thread, args=())
        t.daemon = True
        t.start()

    def update_thread(self):
        """Thread to run for update"""
        self.parent.button_activator.activate.emit(False)
        hrange = self.ls.read_heater_range()
        if hrange > 1:
            hstring = f'{int(hrange)} W'
        elif not hrange:
            hstring = 'Off'
        else:
            hstring = f'{int(hrange * 1000)} mW'
        self.heaterRangeChoice.setCurrentIndex(self.heater_range_choices.index(hstring))
        self.parent.button_activator.activate.emit(True)


class BoxTemplate:
    def __init__(self):
        self.button = QPushButton()
        self.button.setText("Apply")
        self.button.setStyleSheet("QPushButton{font-weight : bold}")
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.set)

    @Slot()
    def set(self):
        t = threading.Thread(target=self.set_thread, args=())
        t.start()

    def set_thread(self):
        pass


class SpinBoxTemplate(BoxTemplate, QDoubleSpinBox):
    def __init__(self, precision: int = 1, maximum: float = None):
        super(self.__class__, self).__init__()
        self.setDecimal(precision)
        if maximum:
            self.setMaximum(maximum)


class RampSpeedBox(SpinBoxTemplate):
    def __init__(self, parent: ControlTab):
        super(self.__class__, self).__init__(precision=1, maximum=100.0)
        self.parent = parent

    def set_thread(self):
        self.parent.button_activator.activate.emit(False)
        print("Setting ramp speed")
        self.parent.ls.set_ramp_speed(self.value())
        print(f"Set ramp speed to {self.text()}")
        self.parent.button_activator.activate.emit(True)


class SetpointBox(SpinBoxTemplate):
    def __init__(self, parent: ControlTab):
        super(self.__class__, self).__init__(precision=2, maximum=400.00)
        self.parent = parent

    def set_thread(self):
        self.parent.button_activator.activate.emit(False)
        print("Setting setpoint")
        self.parent.ls.set_setpoint(self.value())
        print(f"Set setpoint to {self.text()}")
        self.parent.button_activator.activate.emit(True)


class PidBox(BoxTemplate):
    def __init__(self, parent: ControlTab):
        super(self.__class__, self).__init__()
        self.parent = parent
        self.p_box = QDoubleSpinBox()
        self.i_box = QDoubleSpinBox()
        self.d_box = QDoubleSpinBox()
        pid = [self.p_box, self.i_box, self.d_box]

        for box in pid:
            box.setDecimals(1)
            box.setMaximum(1000.0)

    def set_thread(self):
        self.parent.button_activator.activate.emit(False)
        print("Setting PID")
        p = self.p_box.value()
        i = self.i_box.value()
        d = self.d_box.value()
        self.parent.ls.set_pid(p, i, d)
        print(f"Set PID to {p}, {i}, {d}")


class MessageBox(BoxTemplate, QLineEdit):
    def __init__(self, parent: ControlTab):
        super(self.__class__, self).__init__(self)
        self.parent = parent
        self.button.setText("Send")             # Change button from Set to Send

        # add a clear button
        self.clear_button = QPushButton()
        self.clear_button.setText("Clear")
        self.clear_button.setFixedWidth(100)
        self.return_box = QLineEdit()
        self.return_box.setReadOnly(True)

    def set_thread(self):
        pass


    #self.sendLs = qtw.QLineEdit()
    #self.sendLsButton = qtw.QPushButton()
    #self.sendLsButton.setText('Send')
    #self.sendLsButton.setStyleSheet("QPushButton{font-weight : bold}")
    #self.sendLsButton.setFixedWidth(100)
    #self.sendLsButton.clicked.connect(self.send_ls)
    #self.sendLsReset = qtw.QPushButton()
    #self.sendLsReset.setText('Reset')
    #self.sendLsReset.setFixedWidth(100)
    #self.sendLsReset.clicked.connect(self.send_ls_reset)