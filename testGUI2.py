import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QFileDialog, QDialog, QVBoxLayout, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


class AppFile(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.openFileNameDialog()
        self.openFileNamesDialog()
        self.saveFileDialog()

        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, a = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName,a)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


class AppInput(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 input dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.getInputs()

        # self.getInteger()
        # self.getText()
        # self.getDouble()
        # self.getChoice()

        self.show()

    def getInputs(self):
        i, okPressed = QInputDialog.getInt(self, "Get integer", "Percentage:", 28, 0, 100, 1)
        if okPressed:
            print(i)

        d, okPressed = QInputDialog.getDouble(self, "Get double", "Value:", 10.50, 0, 100, 10)
        if okPressed:
            print(d)

        items = ("Red", "Blue", "Green")
        item, okPressed = QInputDialog.getItem(self, "Get item", "Color:", items, 0, False)
        if ok and item:
            print(item)

        text, okPressed = QInputDialog.getText(self, "Get text", "Your name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            print(text)



    def getInteger(self):
        i, okPressed = QInputDialog.getInt(self, "Get integer", "Percentage:", 28, 0, 100, 1)
        if okPressed:
            print(i)

    def getDouble(self):
        d, okPressed = QInputDialog.getDouble(self, "Get double", "Value:", 10.50, 0, 100, 10)
        if okPressed:
            print(d)

    def getChoice(self):
        items = ("Red", "Blue", "Green")
        item, okPressed = QInputDialog.getItem(self, "Get item", "Color:", items, 0, False)
        if ok and item:
            print(item)

    def getText(self):
        text, okPressed = QInputDialog.getText(self, "Get text", "Your name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            print(text)


class AppH(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 layout - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 500
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        box1 = self.createHorizontalLayout()
        box2 = self.createHorizontalLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(box1)
        windowLayout.addWidget(box2)
        self.setLayout(windowLayout)

        self.show()

    def createHorizontalLayout(self):
        horizontalGroupBox = QGroupBox("What is your favorite color?")
        layout = QHBoxLayout()

        buttonBlue = QPushButton('Blue', self)
        buttonBlue.clicked.connect(self.on_click)
        layout.addWidget(buttonBlue)

        buttonRed = QPushButton('Red', self)
        buttonRed.clicked.connect(self.on_click)
        layout.addWidget(buttonRed)

        buttonGreen = QPushButton('Green', self)
        buttonGreen.clicked.connect(self.on_click)
        layout.addWidget(buttonGreen)

        horizontalGroupBox.setLayout(layout)
        return horizontalGroupBox

    @pyqtSlot()
    def on_click(self):
        print('PyQt5 button click')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppFile()
    sys.exit(app.exec_())