import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from start_meas_dialog import StartMeasDialog
import threading
import client_tools
import socket
import time
import datetime
import numpy as np


print_lock = threading.Lock()


class WriteThread(QThread):
    output = pyqtSignal(str)

    def write(self, msg):
        self.output.emit(msg)


class ControllerDataThread(QThread):
    output = pyqtSignal(str, str, str, str)

    def send(self, temperature, heater_output, setpoint, ramp_status):
        self.output.emit(temperature, heater_output, setpoint, ramp_status)


class PlotterThread(QThread):
    output = pyqtSignal()

    def updatePlots(self):
        self.output.emit()


class MeasureTab(qtw.QWidget):
    def __init__(self, parent, base_path):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.base_path = base_path

        self.server = None              # will be the socket
        self.dialog = None              # will be the dialog box widget for inputting data taking info
        self.server_thread = None       # will be a thread for running the socket server for GPIB communication
        self.data_thread = None         # will be a thread for taking data
        self.update_plots = None        # will be a thread to queue updating the plot
        self.date_time_start = None     # will be established when data file starts: datetime.datetime.fromtimestamp()
        self.time_start = None          # will be established when data file starts: time.time()

        self.running = False
        self.paused = False

        """Threading stuff so that data can be written to GUI"""
        self.write_thread = WriteThread()
        # self.write_thread.finished.connect()
        self.write_thread.output.connect(self.writeFromThread)
        self.update_controller_thread = None        # Need to set this up AFTER Control tab is generated

        """Create First Tab"""
        self.layout = qtw.QVBoxLayout(self)

        """Make Text Box for data to dump"""
        self.measureTextStream = qtw.QTextEdit()
        self.measureTextStream.setReadOnly(True)
        self.measureTextStream.setFont(QFont('Arial', 12))
        # self.measureTextStream.textCursor().insertText('')
        self.layout.addWidget(self.measureTextStream)

        """Add Bottom Row of Buttons"""
        self.bottomRow = qtw.QHBoxLayout()
        # self.bottomRow.direction(qtw.QBoxLayout.LeftToRight)
        self.bottomRow.addStretch(1)

        self.buttonNewData = qtw.QPushButton("Start New Data File")
        self.buttonNewData.clicked.connect(self.startNewData)

        self.stackPlayPause = qtw.QStackedWidget(self)
        self.stackPlayPause.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Maximum)  # fixes size issue
        self.buttonPauseData = qtw.QPushButton("Pause")
        self.buttonPauseData.clicked.connect(self.pauseData)
        self.buttonPauseData.setEnabled(False)
        self.buttonContinue = qtw.QPushButton("Continue")
        self.buttonContinue.clicked.connect(self.continueData)
        self.stackPlayPause.addWidget(self.buttonPauseData)
        self.stackPlayPause.addWidget(self.buttonContinue)

        self.buttonStop = qtw.QPushButton("Stop")
        self.buttonStop.clicked.connect(self.stopData)
        self.buttonStop.setEnabled(False)

        self.bottomRow.addWidget(self.buttonStop)
        self.bottomRow.addWidget(self.stackPlayPause)
        self.bottomRow.addWidget(self.buttonNewData)

        self.layout.addLayout(self.bottomRow)

        self.setLayout(self.layout)
        self.write('Dielectric spectroscopy data acquisition GUI')
        self.write('created by Teddy Tortorici 2021')
        self.write('Must have prerequisite drivers and libraries installed (see READ ME)')
        self.write('To begin a new data file, click "Start New Data" or press Ctrl+N')

    def write(self, text):
        self.write_thread.write(text)

    def writeFromThread(self, text):
        self.measureTextStream.append(text)
        self.measureTextStream.verticalScrollBar().setValue(self.measureTextStream.verticalScrollBar().maximum())

    @pyqtSlot()
    def startNewData(self):
        if self.running:
            self.stopData()
        self.dialog = StartMeasDialog(self.base_path)
        self.dialog.exec()
        if self.dialog.result() == qtw.QDialog.Accepted:
            self.running = True
            self.paused = False

            self.time_start = time.time()
            self.date_time_start = datetime.datetime.fromtimestamp(time.time())
            self.write('Starting Data File on {}/{}/{} at {}:{}:{}'.format(self.date_time_start.month,
                                                                           self.date_time_start.day,
                                                                           self.date_time_start.year,
                                                                           self.date_time_start.hour,
                                                                           self.date_time_start.minute,
                                                                           self.date_time_start.second))
            self.buttonPauseData.setEnabled(True)
            self.buttonStop.setEnabled(True)
            self.parent.parent.pauseButton.setEnabled(True)
            self.parent.parent.stopButton.setEnabled(True)
            self.server_thread = threading.Thread(target=self.server_main, args=())
            self.server_thread.start()
            time.sleep(0.5)
            self.data_thread = threading.Thread(target=self.takeData, args=())
            self.data_thread.start()

    def takeData(self):
        time.sleep(0.2)
        units = ['s', 'K', 'pF', '', 'V', 'Hz']
        expected_lens = [22, 6, 8, 8, 2, 4]
        while self.running:
            time.sleep(1)
            while not self.paused:
                msg = client_tools.send('Running')
                print(msg)
                data = [float('%.11f' % (time.time()-self.time_start)),
                        float('%.2f' % (np.random.rand() * 300.)),
                        float('%.6f' % (np.random.rand() * 1.2)), float('%.6f' % (np.random.rand() * 1e-3)),
                        1, 1000]
                msgout = ''
                for item, unit, exp_len in zip(data, units, expected_lens):
                    msgout += ' ' * (exp_len+10-len(str(item)))
                    msgout += str(item)
                    if unit:
                        msgout += f' [{unit}]'
                    msgout += ', '
                msgout = msgout.strip(', ') + ';'
                self.write(msgout)
                self.update_controller_thread.send('%.2f' % (np.random.rand() * 300.),
                                                   '%.2f' % (np.random.rand() * 100.),
                                                   '%.2f' % (np.random.rand() * 300.),
                                                   np.random.choice(['Off', 'On']))
                self.update_plots.updatePlots()
                time.sleep(3)

    @pyqtSlot()
    def pauseData(self):
        self.paused = True
        self.write('Data taking paused.')
        self.stackPlayPause.setCurrentWidget(self.buttonContinue)
        self.parent.parent.pauseButton.setEnabled(False)
        self.parent.parent.continueButton.setEnabled(True)
        # client_tools.send('WHOOOO')

    @pyqtSlot()
    def continueData(self):
        self.paused = False
        self.write('Data taking continued:')
        self.stackPlayPause.setCurrentWidget(self.buttonPauseData)
        self.parent.parent.pauseButton.setEnabled(True)
        self.parent.parent.continueButton.setEnabled(False)

    @pyqtSlot()
    def stopData(self):
        stopQ = qtw.QMessageBox.question(self, 'Stopping Data', 'Are you sure you would like to end this data file?',
                                         qtw.QMessageBox.Yes | qtw.QMessageBox.Cancel, qtw. QMessageBox.Cancel)
        if stopQ == qtw.QMessageBox.Yes:
            self.paused = True
            self.running = False
            self.write('Data acquisition stopped.')
            self.stop()
            self.buttonNewData.setEnabled(True)
            self.buttonStop.setEnabled(False)
            self.stackPlayPause.setCurrentWidget(self.buttonPauseData)
            self.buttonPauseData.setEnabled(False)
            self.parent.parent.pauseButton.setEnabled(False)
            self.parent.parent.continueButton.setEnabled(False)
            self.parent.parent.stopButton.setEnabled(False)

    def server_main(self):  # gpib_comm):
        host = "localhost"
        port = 62535
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        print("socket binded to port", port)

        # put the socket into listening mode
        self.server.listen(5)
        print("socket is listening")

        # a forever loop until client wants to exit
        while self.running:
            # establish connection with client
            c, addr = self.server.accept()

            # lock acquired by client
            print_lock.acquire()
            print('Connected to :', addr[0], ':', addr[1], time.ctime(time.time()))

            # Start a new thread and return its identifier
            while True:
                # message received from client
                msg_client = c.recv(1024)
                msg_client = msg_client.decode('ascii')
                if msg_client == "shutdown":
                    self.running = False
                    print_lock.release()
                    c.close()
                    break
                elif not msg_client:
                    print('unlock thread')
                    # lock released on exit
                    print_lock.release()
                    c.close()
                    break
                else:
                    # parse message
                    # msg_out = gpib_comm.parse(msg_client.decode('ascii'))
                    msg_out = f"Got: {msg_client}"
                    print(msg_out)
                    c.send(msg_out.encode('ascii'))
        self.server.close()

    def init_controller_updates(self):
        self.update_controller_thread = ControllerDataThread()
        self.update_controller_thread.output.connect(self.parent.tabCont.update_values)
        self.update_plots = PlotterThread()
        self.update_plots.output.connect(self.parent.tabPlot.updatePlots)

    def stop(self):
        client_tools.send('shutdown')
        print('stopping data')
        self.server = None
        self.server_thread = None
        print('stopped')
