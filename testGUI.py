import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import sys


class App(qtw.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Application'
        self.left = 10
        self.top = 35
        self.width = 800
        self.height = 800
        self.initUI()

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        toolsMenu = mainMenu.addMenu('Tools')
        exitButton = qtw.QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.quit)
        fileMenu.addAction(exitButton)

        # Create textbox
        self.textbox = qtw.QLineEdit(self)
        self.textbox.move(20, 40)
        self.textbox.resize(280, 40)
        # Create a button in the window
        self.button = qtw.QPushButton('Show Text', self)
        self.button.move(20, 100)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)

        self.choice = qtw.QRadioButton('qq', self)
        self.choice.move(20, 130)

        self.table_widget = TableWidget(self)
        # self.setCentralWidget(self.table_widget)
        self.table_widget.move(20, 300)
        self.table_widget.resize(300, 300)

        self.show()

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        qtw.QMessageBox.question(self, 'Message', 'You typed: ' + textboxValue, qtw.QMessageBox.Ok, qtw.QMessageBox.Ok)
        self.textbox.setText("")

    def quit(self):
        exitQ = qtw.QMessageBox.question(self, 'Exiting', 'Would you like to exit the program?',
                                         qtw.QMessageBox.Yes | qtw.QMessageBox.Cancel, qtw. QMessageBox.Cancel)
        if exitQ == qtw.QMessageBox.Yes:
            print('Exiting')
            self.close()
        else:
            print('Continuing Program')


class TableWidget(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.layout = qtw.QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = qtw.QTabWidget()
        self.tab1 = qtw.QWidget()
        self.tab2 = qtw.QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "tab 1")
        self.tabs.addTab(self.tab2, "tab 2")

        # Create First Tab
        self.tab1.layout = qtw.QVBoxLayout(self)
        self.pushButton1 = qtw. QPushButton("This is a button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(selfself):
        pritn("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(),
                  currentQTableWidgetItem.text())


class Dialog(qtw.QDialog):

    def slot_method(self):
        print('slot method called.')

    def __init__(self):
        super(Dialog, self).__init__()

        button = qtw.QPushButton("Click")
        button.clicked.connect(self.slot_method)

        mainLayout = qtw.QVBoxLayout()
        mainLayout.addWidget(button)

        self.setLayout(mainLayout)
        self.setWindowTitle("Button Example - pythonspot.com")


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # dialog = Dialog()
    ex = App()
    sys.exit(app.exec_())
