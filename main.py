import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import sys
import yaml
import get
import os
import glob


class App(qtw.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy-2')
        self.lj_chs = []  # will be used later
        self.path = self.base_path  # will be added on to later

        """LOAD PRESETS"""
        yaml_fname = max(glob.glob(os.path.join(self.base_path, 'presets', '*yml')), key=os.path.getctime)
        yaml_f = os.path.join(self.base_path, 'presets', yaml_fname)
        # print(f'\n\n{yaml_f}\n\n')
        with open(yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        """MENU BAR"""
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')

        exitButton = qtw.QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.quit)
        fileMenu.addAction(exitButton)

        """WINDOW PROPERTIES"""
        self.setWindowTitle('Dielectric Spectroscopy')
        self.left = 10
        self.top = 35
        self.width = 1000
        self.height = 800
        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tabs = MainTabs(self)
        self.setCentralWidget(self.tabs)

        self.show()

    def quit(self):
        exitQ = qtw.QMessageBox.question(self, 'Exiting', 'Are you sure you would like to quit?',
                                         qtw.QMessageBox.Yes | qtw.QMessageBox.Cancel, qtw. QMessageBox.Cancel)
        if exitQ == qtw.QMessageBox.Yes:
            print('Exiting')
            self.close()


class MainTabs(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.layout = qtw.QVBoxLayout(self)

        """Initialize tab screen"""
        self.tabs = qtw.QTabWidget()
        self.tabMeas = qtw.QWidget()
        self.tabPlot = qtw.QWidget()
        self.tabCont = qtw.QWidget()

        """Add tabs"""
        self.tabs.addTab(self.tabMeas, "Measure")
        self.tabs.addTab(self.tabPlot, "Plot")
        self.tabs.addTab(self.tabCont, "Control")

        """Create First Tab"""
        self.tabMeas.layout = qtw.QVBoxLayout(self)

        """Make Text Box for data to dump"""
        self.measureTextStream = qtw.QTextEdit()
        self.measureTextStream.setReadOnly(True)
        # self.measureTextStream.textCursor().insertText('')
        self.tabMeas.layout.addWidget(self.measureTextStream)

        """Add Bottom Row of Buttons"""
        self.bottomRow = qtw.QHBoxLayout()
        self.bottomRow.addStretch(1)
        self.buttonNewData = qtw.QPushButton("Start New Data File")
        self.buttonNewData.clicked.connect(self.startNewData)

        self.stackPlayPause = qtw.QStackedWidget(self)
        self.buttonPauseData = qtw.QPushButton("Pause")
        self.buttonPauseData.clicked.connect(self.pauseData)
        self.buttonContinue = qtw.QPushButton("Continue")
        self.buttonContinue.clicked.connect(self.continueData)
        self.stackPlayPause.addWidget(self.buttonPauseData)
        self.stackPlayPause.addWidget(self.buttonContinue)

        self.bottomRow.addWidget(self.buttonNewData)

        #self.tabMeas.layout.addStretch(1)
        self.tabMeas.layout.addLayout(self.bottomRow)

        # self.tabMeas.layout.addWidget(self.newDataButton)
        self.tabMeas.setLayout(self.tabMeas.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def write(self, text):
        self.measureTextStream.textCursor().insertText('\n' + text)
        self.measureTextStream.verticalScrollBar().setValue(self.measureTextStream.verticalScrollBar().maximum())

    @pyqtSlot()
    def startNewData(self):
        self.write('start data')
        self.bottomRow.removeWidget(self.buttonNewData)
        self.bottomRow.addWidget(self.stackPlayPause)
        self.bottomRow.addWidget(self.buttonNewData)
        # self.stackPlayPause.setSizePolicy(40, 15)

    @pyqtSlot()
    def pauseData(self):
        self.write('data paused')
        self.stackPlayPause.setCurrentWidget(self.buttonContinue)

    @pyqtSlot()
    def continueData(self):
        self.write('data continued')
        self.stackPlayPause.setCurrentWidget(self.buttonPauseData)

    @pyqtSlot()
    def on_click(selfself):
        pritn("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(),
                  currentQTableWidgetItem.text())


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # dialog = Dialog()
    ex = App()
    sys.exit(app.exec_())
