import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import sys
import yaml


class App(qtw.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.yaml_f = 'server_settings.yml'
        with open(self.yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        if preset['ah']:
            self.bridge = 0         # AH
        else:
            self.bridge = 1         # HP

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
        self.tabs.move(5, 20)
        self.tabs.resize(self.width - 10, self.height - 10)
        # label = qtw.QLabel(f'the bridge is set to {self.bridge}', self)
        # label.move(10, 10)
        '''# Create textbox
        self.textbox = qtw.QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)
        # Create a button in the window
        self.button = qtw.QPushButton('Show Text', self)
        self.button.move(20, 80)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)

        self.choice = qtw.QRadioButton('qq', self)
        self.choice.move(20, 120)'''
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

        # Initialize tab screen
        self.tabs = qtw.QTabWidget()
        self.tabMeas = qtw.QWidget()
        self.tabPlot = qtw.QWidget()
        self.tabCont = qtw.QWidget()
        # self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tabMeas, "Measure")
        self.tabs.addTab(self.tabPlot, "Plot")
        self.tabs.addTab(self.tabCont, "Control")

        # Create First Tab
        self.tabMeas.layout = qtw.QVBoxLayout(self)
        # self.pushButton1 = qtw. QPushButton("This is a button")
        # self.tab1.layout.addWidget(self.pushButton1)
        # self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

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
