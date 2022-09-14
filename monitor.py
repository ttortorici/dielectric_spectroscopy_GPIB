"""
Simple Monitor to mimic AH front panel

@author: Teddy Tortorici
"""

import os
import sys
import threading

from PySide6.QtWidgets import (QMainWindow, QApplication, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QLabel, QRadioButton, QButtonGroup)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont
import gui.icons as icon
from comm.socket_client import send as send_client
from comm.devices.ah2700 import Client as Bridge
from comm.server import GpibServer


class DisplayWidget(QLineEdit):
    def __init__(self, parent: QWidget, label: str = ""):
        super(DisplayWidget, self).__init__()
        self.parent = parent
        with open(os.path.join("gui", "stylesheets", "display.css"), "r") as f:
            self.setStyleSheet(f.read())

        self.setFont(QFont("Arial", 26))
        self.label = QLabel(label)
        self.label.setFixedWidth(225)
        self.label.setFont(QFont("Arial", 26))
        self.label.setAlignment(Qt.AlignCenter)

        self.setReadOnly(True)
        self.row_layout = QHBoxLayout()
        self.row_layout.addWidget(self.label)
        self.row_layout.addWidget(self)


class InputWidget(QLineEdit):
    def __init__(self, parent):
        super(InputWidget, self).__init__()
        self.parent = parent
        with open(os.path.join("gui", "stylesheets", "input_line.css"), "r") as f:
            self.setStyleSheet(f.read())


class FrequencyWidget(QButtonGroup):
    def __init__(self, parent):
        super(FrequencyWidget, self).__init__()
        self.parent = parent
        options = ("100 Hz", "400 Hz", "500 Hz", "600 Hz", "700 Hz", "800 Hz",
                   "1 kHz", "1.4 kHz", "1.6 kHz", "2 kHz", "2.4 kHz", "4 kHz",
                   "10 kHz", "12 kHz", "14 kHz", "16 kHz", "20 kHz")
        self.buttons = [None] * len(options)

        self.col_layout = QVBoxLayout()
        self.col_layout.setAlignment(Qt.AlignCenter)
        for ii, option in enumerate(options):
            widget = QRadioButton(option)
            if option in ("400 Hz", "1.4 kHz", "14 kHz"):
                widget.setStyleSheet("color: #FFFFAA; font: bold; font-size: 18px;")
            else:
                widget.setStyleSheet("color: #FFFFFF; font: arial; font-size: 18px;")
            self.buttons[ii] = widget
            self.addButton(widget, ii)
            self.col_layout.addWidget(widget)
        self.buttons[7].setChecked(True)
        self.buttonClicked.connect(self.button_press)

    @Slot()
    def button_press(self):
        self.parent.bridge.write(f"FR {self.value():d}")

    def value(self):
        text = self.button(self.checkedId()).text().rstrip("Hz")
        if text[-1] == "k":
            frequency = int(float(text.rstrip(" k")) * 1000)
        else:
            frequency = int(text)
        return frequency


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.server = GpibServer()
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.start()
        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.daemon = True

        self.bridge = Bridge()
        self.bridge.format(notation="FLOAT", labeling="OFF", ieee="ON", fwidth="FIX")

        main_layout = QHBoxLayout(self)

        display_layout = QVBoxLayout()

        display_keys = ("Frequency", "Capacitance", "Loss Tangent", "RMS Voltage")
        self.displays = dict(zip(display_keys, [DisplayWidget(self, key) for key in display_keys]))

        for key in display_keys:
            display_layout.addLayout(self.displays[key].row_layout)

        self.frequency_options = FrequencyWidget(self)

        main_layout.addLayout(display_layout)
        main_layout.addLayout(self.frequency_options.col_layout)

        self.setLayout(main_layout)

        self.bridge.set_frequency(self.frequency_options.value())
        self.bridge.set_ave(7)
        self.run_thread.start()

    def update_displays(self, frequency: str, capacitance: str, loss: str, voltage: str):
        self.displays["Frequency"].setText(frequency)
        self.displays["Capacitance"].setText(capacitance)
        self.displays["Loss Tangent"].setText(loss)
        self.displays["RMS Voltage"].setText(voltage)

    def run(self):
        while True:
            front_panel = self.bridge.read_front_panel()
            self.update_displays(*front_panel)


class MainWindow(QMainWindow):
    width = 1200
    height = 650

    def __init__(self):
        """
        Main window that contains 3 tabs in a navigation widget. These tabs are for taking data, plotting data,
        and controlling devices.
        """
        QMainWindow.__init__(self)

        with open(os.path.join("gui", "stylesheets", "main.css"), "r") as f:
            self.setStyleSheet(f.read())

        self.force_quit = True  # when quit properly, this will be changed to false
        self.file_open = False

        self.socket_server = None
        self.server_thread = None
        self.data_thread = None

        """WINDOW PROPERTIES"""
        self.setWindowTitle("Data Acquisition App")
        self.resize(MainWindow.width, MainWindow.height)

        self.setWindowIcon(icon.custom('app.png'))

        self.main = MainWidget()
        self.setCentralWidget(self.main)

    @Slot()
    def quit(self):
        """Exit program"""
        exit_question = QMessageBox.critical(self, 'Exiting', 'Are you sure you would like to quit?',
                                             QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if exit_question == QMessageBox.Yes:
            send_client("shutdown")
            self.main.server_thread.join()
            self.force_quit = False
            print('Exiting')
            self.close()

    @Slot()
    def closeEvent(self, event):
        """Overrides closeEvent so that there is no force quit"""
        if self.force_quit:
            event.ignore()
            self.quit()
        else:
            event.accept()

    @Slot()
    def get_help(self):
        """Opens HELP Prompt"""
        self.help.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
