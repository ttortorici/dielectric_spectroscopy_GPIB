"""
Simple Monitor to mimic AH front panel

@author: Teddy Tortorici
"""

import os
import sys
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
        options = (QRadioButton("400 Hz"),)

        self.col_layout = QVBoxLayout()
        for widget in options:
            self.col_layout.addWidget(widget)




class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        # self.server = GpibServer()
        # self.server.run()

        # self.bridge = Bridge()
        main_layout = QHBoxLayout(self)

        display_layout = QVBoxLayout()

        displays = (DisplayWidget(self, "Frequency"),
                    DisplayWidget(self, "Capacitance"),
                    DisplayWidget(self, "Loss Tangent"),
                    DisplayWidget(self, "RMS Voltage"))

        for display_widget in displays:
            display_layout.addLayout(display_widget.row_layout)

        self.frequency_options = FrequencyWidget(self)

        main_layout.addLayout(display_layout)
        main_layout.addLayout(self.frequency_options.col_layout)

        self.setLayout(main_layout)


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

        self.force_quit = True              # when quit properly, this will be changed to false
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
            # send_client("shutdown")
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
