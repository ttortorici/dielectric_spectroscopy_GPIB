import PyQt5.QtWidgets as qtw
# from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import sys


class App(qtw.QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Application'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # ahButton =
        buttonReply = qtw.QMessageBox.question(self, 'Capacitive Bridge', 'What Bridge Would you like to use?',
                                               #qtw.addButton('AH'), qtw.addButton('HP'))
                                               qtw.QMessageBox.Yes | qtw.QMessageBox.No, qtw.QMessageBox.No)
        ahButton = buttonReply.addButton('AH', buttonReply.Yes)
        hpButton = buttonReply.addButton('HP', buttonReply.No)
        if buttonReply == qtw.QMessageBox.Yes:
            print('Yes clicked')
        else:
            print('No clicked')

        # Create textbox
        self.textbox = qtw.QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)
        # Create a button in the window
        self.button = qtw.QPushButton('Show Text', self)
        self.button.move(20, 80)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        qtw.QMessageBox.question(self, 'Message', 'You typed: ' + textboxValue, qtw.QMessageBox.Ok, qtw.QMessageBox.Ok)
        self.textbox.setText("")


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