"""
Main script to run the GUI application

@author: Teddy Tortorici
"""

import get
import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QTabWidget, QToolBar
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from gui.tabs.data import DataTab
from gui.tabs.plot import PlotTab
from gui.tabs.control import ControlTab
from gui.dialogs.help import HelpPrompt
import gui.icons as icon


class MainWindow(QMainWindow):

    width = 1200
    height = 650

    def __init__(self):
        """
        Main window that contains 3 tabs in a navigation widget. These tabs are for taking data, plotting data,
        and controlling devices.
        """
        QMainWindow.__init__(self)

        with open(os.path.join("gui", "stylesheet.css"), "r") as f:
            self.setStyleSheet(f.read())

        self.data_base_path = os.path.join(get.google_drive(), "Dielectric_data", "Teddy-2",)  # base path to data files

        self.force_quit = True              # when quit properly, this will be changed to false
        self.file_open = False

        self.socket_server = None
        self.server_thread = None
        self.data_thread = None

        """WINDOW PROPERTIES"""
        self.setWindowTitle("Data Acquisition App")
        self.resize(MainWindow.width, MainWindow.height)

        self.setWindowIcon(icon.custom('app.png'))

        """NAVIGATION TABS"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Tabs
        self.data_tab = DataTab(self)
        self.plot_tab = PlotTab(self)
        self.control_tab = ControlTab(self)
        self.control_tab.setStyleSheet("background-color: rgb(43, 43, 32);"
                                       "color: rgb(255, 255, 255)")
        tabs = [(self.data_tab, "&Data"),
                (self.plot_tab, "&Plots"),
                (self.control_tab, "&Control")]

        # Add tabs
        for tab, name in tabs:
            self.tabs.addTab(tab, name)

        """MENU BAR"""
        main_menu = self.menuBar()

        # File, Data, and Help drop down menus
        file_menu = main_menu.addMenu('&File')
        data_menu = main_menu.addMenu('&Data')
        help_menu = main_menu.addMenu('&Help')

        self.help = HelpPrompt()

        """MENU ACTIONS"""
        # File menu actions
        self.new_file_action = QAction(icon.built_in(self, 'FileIcon'), '&New Data File', self)
        self.new_file_action.setShortcut('CTRL+N')
        self.new_file_action.triggered.connect(self.data_tab.make_new_file)
        self.open_file_action = QAction(icon.built_in(self, 'DirIcon'), '&Open Data File', self)
        self.open_file_action.setShortcut('CTRL+O')
        self.open_file_action.triggered.connect(self.data_tab.open_file)
        self.exit_action = QAction(icon.built_in(self, 'BrowserStop'), 'E&xit', self)
        self.exit_action.setShortcut('CTRL+Q')
        self.exit_action.triggered.connect(self.quit)
        # Data menu actions
        self.play_action = QAction(icon.custom("play.png"), 'Take &Data', self)
        self.play_action.setShortcut('CTRL+SPACE')
        self.play_action.triggered.connect(self.data_tab.continue_data)
        self.pause_action = QAction(icon.custom("pause.png"), 'Pause &Data', self)
        self.pause_action.setShortcut('CTRL+SPACE')
        self.pause_action.triggered.connect(self.data_tab.pause_data)
        self.stop_action = QAction(icon.custom("stop.png"), '&Stop Data', self)
        self.stop_action.setShortcut('CTRL+W')
        self.stop_action.triggered.connect(self.data_tab.stop)
        # Help menu actions
        self.about_action = QAction(icon.built_in(self, 'MessageBoxQuestion'), '&About', self)
        self.about_action.setShortcut('CTRL+/')
        self.about_action.triggered.connect(self.get_help)

        file_actions = [self.new_file_action, self.open_file_action, self.exit_action]
        data_actions = [self.play_action, self.pause_action, self.stop_action]
        help_actions = [self.about_action]

        """ADD ACTIONS to MENUS and TOOLBARS"""
        toolbar = QToolBar()
        for action in file_actions:
            if action.text() == "E&xit":
                file_menu.addSeparator()
            else:
                toolbar.addAction(action)
            file_menu.addAction(action)
        toolbar.addSeparator()
        for action in data_actions:
            data_menu.addAction(action)
            toolbar.addAction(action)
        toolbar.addSeparator()
        for action in help_actions:
            help_menu.addAction(action)
            toolbar.addAction(action)

        """ADD ACTIONS TO TOOLBAR"""
        self.addToolBar(toolbar)

        """Disable the following actions on start up"""
        for action in data_actions:
            action.setEnabled(False)

    @Slot()
    def quit(self):
        """Exit program"""
        stop = True
        if self.data_tab.active_file:
            stop = self.data_tab.stop()
        if stop:
            exit_question = QMessageBox.critical(self, 'Exiting', 'Are you sure you would like to quit?',
                                                 QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
            if exit_question == QMessageBox.Yes:
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
