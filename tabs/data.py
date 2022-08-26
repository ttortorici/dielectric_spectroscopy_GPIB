"""
A tab widget for taking data in app.py

@author: Teddy Tortorici
"""

import os.path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QStackedWidget, QSizePolicy,
                               QDialog, QMessageBox, QFileDialog, QMainWindow)
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont, QTextCursor
from dialogs.new_file import NewFileDialog
import gui.icons as icon
from gui.signalers import Signaler, MessageSignaler
import data_files
from comm.server import GpibServer
from comm.socket_client import send as send_client
import threading
import time
import datetime


class TextStream(QTextEdit):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setReadOnly(True)
        self.setFont(DataTab.font)

    @Slot(str)
    def write(self, text: str):
        """Writes to GUI from the write_thread object attribute"""
        # print(f'received "{text}" fom thread')
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)

        # make the scroll bar scroll with the new text as it fills past the size of the window
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class DataTab(QWidget):

    font = QFont("Arial", 12)

    def __init__(self, parent: QMainWindow):
        """
        Tab for managing the current data file
        :param parent: Is the MainWindow() object
        """
        QWidget.__init__(self)
        self.parent = parent

        self.gpib_server = GpibServer(do_print=False)

        self.dialog = None
        self.data = None            # will be an object of a data file from data_file2.py

        self.server_thread = None   # will create thread on data file start up
        self.data_thread = None     # will create thread on data file start up

        self.running = False
        self.active_file = False

        """So we can write to the GUI from threads"""
        self.writer_signaler = MessageSignaler()
        self.writer_signaler.signal.connect(self.data_text_stream.write)

        """So we can update plots when new data is taken"""
        self.plot_updater = Signaler()
        self.plot_initializer = MessageSignaler()
        # Moved to activate_data_file()
        # self.plot_updater = PlotUpdaterWidget()
        # self.plot_updater.update.connect(self.parent.plot_tab.update_plots)
        # self.plot_updater.initialize.connect(self.parent.plot_tab.initialize_plots)

        """Create the layout of what goes in this tab"""
        self.layout = QVBoxLayout(self)

        self.data_text_stream = TextStream()     # this will be where data gets printed as it's collected

        self.bottom_row = QHBoxLayout()         # this will be a row to add widgets to bellow the text stream
        self.bottom_row.addStretch(1)

        self.button_new_data = QPushButton("Create New Data File")
        self.button_new_data.setIcon(icon.built_in(self, 'FileIcon'))
        self.button_new_data.clicked.connect(self.make_new_file)

        self.button_open_data = QPushButton("Open Data File")
        self.button_open_data.setIcon(icon.built_in(self, 'DirIcon'))
        self.button_open_data.clicked.connect(self.open_file)

        self.button_play_pause = QStackedWidget(self)
        self.button_play_pause.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.button_pause = QPushButton("Pause Data")
        self.button_pause.setIcon(icon.built_in(self, 'MediaPause'))
        self.button_pause.clicked.connect(self.pause_data)
        self.button_play = QPushButton("Take Data")
        self.button_play.setIcon(icon.built_in(self, 'MediaPlay'))
        self.button_play.clicked.connect(self.continue_data)
        self.button_play.setEnabled(False)
        self.button_pause.setEnabled(False)
        self.button_play_pause.addWidget(self.button_play)
        self.button_play_pause.addWidget(self.button_pause)

        self.button_stop = QPushButton("Stop")
        self.button_stop.setIcon(icon.built_in(self, 'MediaStop'))
        self.button_stop.setEnabled(False)
        self.button_stop.clicked.connect(self.stop)

        # add bottom row widgets to bottom_row
        self.bottom_row.addWidget(self.button_stop)
        self.bottom_row.addWidget(self.button_play_pause)
        self.bottom_row.addWidget(self.button_open_data)
        self.bottom_row.addWidget(self.button_new_data)

        """Add widgets to layout"""
        self.layout.addWidget(self.data_text_stream)
        self.layout.addLayout(self.bottom_row)

    def write(self, text: str, end: str = "\n"):
        """Writes to the GUI by using the write_thread widget"""
        # print(f'sending "{text}" to thread')
        self.writer_signaler.message.emit(text + end)

    @Slot()
    def open_file(self):
        """Open a dialog to find a file to append to"""
        stop = True
        if self.active_file:
            stop = self.stop()
        if stop:
            options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getOpenFileName(self,  # parent
                                                      "Open data file",  # caption
                                                      self.parent.data_base_path,  # directory
                                                      "CSV (*.csv)",  # filters
                                                      options=options)  # dialog options
            if filename:
                # open file and read comment to find what the averaging setting is
                with open(filename, 'r') as f:
                    for ii in range(2):                 # number in range will be which line is stored at the end
                        comment_line = f.readline()
                # see if average is specified in the comment
                self.dialog = FakeDialog()               # with default averaging_entry = 1
                if 'average' in comment_line:
                    ave_num_end = comment_line.index('average') - 1
                    # attempt to read the number of unknown size until it works
                    for ii in range(3):
                        try:
                            self.dialog.averaging_entry = int(comment_line[ave_num_end-ii:ave_num_end])
                            break
                        except ValueError:
                            pass

                self.write(f'Opening file "{filename}"')
                self.write(f'Using averaging setting of {self.dialog.averaging_entry}')
                self.activate_data_file(filename)
                self.data = data_files.CalFile(filename)
                self.data_thread.start()

    @Slot()
    def make_new_file(self):
        """Open a dialog to create a new data file"""
        stopped = True
        if self.active_file:
            stopped = self.stop()
        if stopped:
            self.dialog = NewFileDialog(self.parent.data_base_path)
            self.dialog.exec()

            if self.dialog.result() == QDialog.Accepted:
                creation_time = self.dialog.date
                creation_datetime = datetime.datetime.fromtimestamp(creation_time)
                self.write('Starting new data file on {m:02}/{d:02}/{y:04} at {h:02}:{min:02}:{s}'.format(
                    m=creation_datetime.month,
                    d=creation_datetime.day,
                    y=creation_datetime.year,
                    h=creation_datetime.hour,
                    min=creation_datetime.minute,
                    s=creation_datetime.second))

                """FIND PLACE TO WRITE FILE"""  # "Calibration", "Powder Sample", "Film Sample", "Other"
                if self.dialog.purp_choice == "Calibration":
                    path = os.path.join(self.parent.data_base_path)

                sample_name = self.dialog.sample_name_entry.replace(' ', '_')
                if not sample_name:
                    sample_name = 'none'
                filename = '{sample}_{m:02}-{d:02}-{y:04}_{h:02}-{min:02}-{s}.csv'.format(sample=sample_name,
                                                                                          m=creation_datetime.month,
                                                                                          d=creation_datetime.day,
                                                                                          y=creation_datetime.year,
                                                                                          h=creation_datetime.hour,
                                                                                          min=creation_datetime.minute,
                                                                                          s=creation_datetime.second)
                comment = 'Experiment performed on the {setup} setup with sample: {sample}.'.format(
                    setup=self.dialog.setup_choice_entry,
                    sample=self.dialog.sample_name_entry)
                if self.dialog.averaging_entry > 1:
                    comment += f' Data is taken with {self.dialog.averaging_entry} averages.'
                if self.dialog.calibration_file_entry:
                    comment += f' Using calibration file: {self.dialog.calibration_file_entry}.'
                if self.dialog.comment_entry:
                    comment += f' ... {self.dialog.comment_entry}.'

                file_path = os.path.join(self.parent.data_base_path, filename)
                self.activate_data_file(file_path)
                self.data = data_files.CalFile(file_path, comment)
                self.data_thread.start()

    def activate_data_file(self, filename):
        """Whether we open a file or make a new one, we need to do all these things"""
        self.server_thread = threading.Thread(target=self.gpib_server.run, args=())
        self.data_thread = threading.Thread(target=self.take_data, args=())

        self.plot_updater.signal.connect(self.parent.plot_tab.update_plots)
        self.plot_initializer.signal.connect(self.parent.plot_tab.initialize_plots)
        self.plot_initializer.signal.emit(filename)

        self.active_file = True
        self.button_play.setEnabled(True)
        self.button_pause.setEnabled(True)
        self.button_stop.setEnabled(True)
        self.button_play_pause.setCurrentWidget(self.button_pause)
        self.parent.play_action.setEnabled(False)
        self.parent.pause_action.setEnabled(True)
        self.parent.stop_action.setEnabled(True)
        self.parent.exit_action.setEnabled(False)

        """Start GPIB communication server"""
        self.server_thread.start()
        time.sleep(0.01)

    def take_data(self):
        """This should be ran in a thread"""
        self.running = True
        while self.active_file:
            while self.running:
                data_point = self.data.sweep_frequencies()
                # print(f'Got this as data: {data_point}')
                self.data.write_row(data_point)
                self.write(str(data_point))
                if self.parent.plot_tab.live_plotting:
                    self.plot_updater.signal.emit()

    @Slot()
    def continue_data(self):
        """If data taking is paused, this will unpause it"""
        self.button_play_pause.setCurrentWidget(self.button_pause)
        self.button_pause.setEnabled(True)
        self.parent.pause_action.setEnabled(True)
        self.parent.play_action.setEnabled(False)
        self.running = True

    @Slot()
    def pause_data(self):
        """Pause taking data"""
        self.button_play_pause.setCurrentWidget(self.button_play)
        self.button_play.setEnabled(True)
        self.parent.pause_action.setEnabled(False)
        self.parent.play_action.setEnabled(True)
        self.running = False
        self.write("Paused data taking.")

    @Slot()
    def stop(self):
        """Stop taking data and prepare to close or open or create new data"""
        exit_question = QMessageBox.question(self, 'Stop', 'Are you sure you would like to close this data file?',
                                             QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if exit_question == QMessageBox.Yes:
            self.running = False
            self.active_file = False
            self.data_thread.join()
            self.button_stop.setEnabled(False)
            self.button_play_pause.setCurrentWidget(self.button_play)
            self.button_play.setEnabled(False)
            self.button_pause.setEnabled(False)
            self.parent.play_action.setEnabled(True)
            self.parent.pause_action.setEnabled(True)
            self.parent.stop_action.setEnabled(True)
            self.parent.exit_action.setEnabled(False)
            send_client('shutdown')
            self.server_thread.join()
            self.write("Closing File")
            self.data = None
            self.dialog = None
            return True
        else:
            return False


class FakeDialog:
    """This is for when we open a file so we can mimic pulling the averaging entry from the dialog for a new file"""
    def __init__(self):
        self.averaging_entry = 1


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    main_window = DataTab(0)
    main_window.show()

    sys.exit(app.exec())
