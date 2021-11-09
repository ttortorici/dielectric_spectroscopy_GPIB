import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from PyQt5.QtGui import QIcon
import sys
import get
import os
from main_tabs import MainTabs


class App(qtw.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy-2')
        self.lj_chs = []  # will be used later
        self.path = self.base_path  # will be added on to later

        self.force_quit = True      # will turn false if quit properly

        """WINDOW PROPERTIES"""
        self.setWindowTitle('Dielectric Spectroscopy')
        self.left = 10
        self.top = 35
        self.width = 1000
        self.height = 800

        self.setWindowIcon(QIcon(os.path.join('icons', 'app.png')))

        self.setGeometry(self.left, self.top, self.width, self.height)

        """NAVIGATION TABS"""
        self.tabs = MainTabs(self, self.base_path)
        self.setCentralWidget(self.tabs)

        """MENU BAR"""
        mainMenu = self.menuBar()

        # File
        fileMenu = mainMenu.addMenu('File')

        newDataButton = qtw.QAction(QIcon(os.path.join('icons', 'new_data.png')), 'New Data Set', self)
        newDataButton.setShortcut('Ctrl+N')
        newDataButton.triggered.connect(self.tabs.tabMeas.startNewData)

        exitButton = qtw.QAction(QIcon(os.path.join('icons', 'quit.png')), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.quit)

        fileMenu.addActions([newDataButton])
        fileMenu.addSeparator()
        fileMenu.addActions([exitButton])

        # Data
        dataMenu = mainMenu.addMenu('Data')

        self.pauseButton = qtw.QAction(QIcon(os.path.join('icons', 'pause.png')), 'Pause', self)
        self.pauseButton.setShortcut('Ctrl+P')
        self.pauseButton.triggered.connect(self.tabs.tabMeas.pauseData)
        self.pauseButton.setEnabled(False)

        self.continueButton = qtw.QAction(QIcon(os.path.join('icons', 'play.png')), 'Continue', self)
        self.continueButton.setShortcut('Ctrl+P')
        self.continueButton.triggered.connect(self.tabs.tabMeas.continueData)
        self.continueButton.setEnabled(False)

        self.stopButton = qtw.QAction(QIcon(os.path.join('icons', 'stop.png')), 'Stop', self)
        self.stopButton.setShortcut('Ctrl+W')
        self.stopButton.triggered.connect(self.tabs.tabMeas.stopData)
        self.stopButton.setEnabled(False)

        dataMenu.addActions([self.pauseButton, self.continueButton, self.stopButton])



        self.show()

    def quit(self):
        if self.tabs.tabMeas.running:
            self.tabs.tabMeas.stopData()
        exitQ = qtw.QMessageBox.question(self, 'Exiting', 'Are you sure you would like to quit?',
                                         qtw.QMessageBox.Yes | qtw.QMessageBox.Cancel, qtw. QMessageBox.Cancel)
        if exitQ == qtw.QMessageBox.Yes:
            self.force_quit = False
            print('Exiting')
            self.close()

    def closeEvent(self, event):
        if self.force_quit:
            self.quit()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # dialog = Dialog()
    ex = App()
    sys.exit(app.exec_())
