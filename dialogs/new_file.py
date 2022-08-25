from PySide6.QtWidgets import (QDialog, QSizePolicy, QGroupBox, QComboBox, QLineEdit, QDialogButtonBox, QFileDialog,
                               QLabel, QSpinBox, QPushButton, QFormLayout, QVBoxLayout, QDoubleSpinBox)
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from gui.icons import custom as custom_icon
import sys
import yaml
import os
import glob
import datetime
import time


def datetime_from_yaml_name(yaml_name):
    return datetime.datetime.fromisoformat(yaml_name.split(os.sep)[-1].lstrip('presets').rstrip('.yml'))


class DropDown(QComboBox):
    def __init__(self, choices: list[str], shortcuts: list[str] = None, label: str = "", whats_this: str = None):
        """
        ComboBox with label and stores it's own information
        :param label: a string that will be placed before the combobox in the form
        :param choices: The labels of the options that appear in the combo box
        :param shortcuts: option shortcuts for storing
        :param whats_this: description
        """
        super(self.__class__, self).__init__()
        self.label = QLabel(label + ":")
        if whats_this:
            self.label.setWhatsThis(whats_this)
        self.choices = choices
        self.shortcuts = shortcuts
        self.addItems(choices)

    def get(self) -> str:
        """
        Get the active entry
        :return: returns the shortcut of the selection if there are shortcuts. Otherwise, it returns the actual value
        """
        if self.shortcuts:
            return self.shortcuts[self.currentIndex()]
        else:
            return self.choices[self.currentIndex()]

    def set(self, option):
        """
        Sets the combobox option based off the shortcut given. If there aren't shortcuts, then it takes the actual value
        instead
        :param option: shortcut or box value
        """
        try:
            self.setCurrentIndex(self.shortcuts.index(option))
        except ValueError:
            self.setCurrentIndex(self.choices.index(option))


class Entry(QLineEdit):
    def __init__(self, label: str = "", whats_this: str = None):
        """
        Create a line edit entry box
        :param label: label to go next to it
        :param whats_this: description
        """
        super(self.__class__, self).__init__()
        self.label = QLabel(label + ":")
        if whats_this:
            self.label.setWhatsThis(whats_this)

    def get(self) -> str:
        """
        get the text that has been entered by the user
        :return: user entered text
        """
        return self.text()

    def set(self, text: str):
        """
        set the text of the box from the software. Overrides current text
        :param text: text to write
        """
        self.setText(text)


class FileButton(QPushButton):
    def __init__(self, base_path: str, title: str = "", label: str = "",
                 whats_this: str = None, filetypes: str = "CSV (*.csv)"):
        """
        Create a button for opening a file
        :param base_path: base path for file dialog
        :param title: Default text of button (and title of dialog window)
        :param label: text to the side
        :param whats_this: description
        :param filetypes: types of files to filter separated by ';;'
        """
        super(self.__class__, self).__init__()
        self.base_path = base_path
        self.title = title
        self.setText(title)
        self.label = QLabel(label + ":")
        if whats_this:
            self.label.setWhatsThis(whats_this)
        self.filetypes = filetypes

        self.filename = None

        self.clicked.connect(self.open_file)

    @Slot()
    def open_file(self):
        """
        Open file dialog and replace button text with the filename
        """
        self.filename, _ = QFileDialog.getOpenFileName(self, self.title, self.base_path,
                                                       f"{self.filetypes};;All Files (*)")
        filename_display = self.filename.lstrip(self.base_path)
        self.setText(filename_display)

    def get(self) -> str:
        """
        Get the filepath
        :return: Will return the filepath given from the button
        """
        if self.filename:
            return self.filename
        elif self.text() == self.title or not self.text():
            return ""
        else:
            return os.path.join(self.base_path, self.text())

    def set(self, text: str):
        self.setText(text)


class IntBox(QSpinBox):
    def __init__(self, label: str = "", whats_this: str = None):
        """
        Create a spinbox for entering integer values
        :param label: Label to the left
        :param whatsthis: Description
        """
        super(self.__class__, self).__init__()
        self.label = QLabel(label + ":")
        if whats_this:
            self.label.setWhatsThis(whats_this)

    def get(self) -> int:
        """
        return the integer value
        :return: The user defined value
        """
        return self.value()

    def set(self, value: int):
        """
        Sets the value in the box
        :param value: an integer value to display
        """
        self.setValue(value)


class FloatBox(QDoubleSpinBox):
    def __init__(self, precision: int = 1, minimum: float = 0., maximum: float = 100.,
                 label: str = "", whats_this: str = None):
        super(self.__class__, self).__init__()
        self.setDecimals(precision)
        self.setMaximum(maximum)
        self.setMinimum(minimum)
        self.label = QLabel(label + ":")
        if whats_this:
            self.label.setWhatsThis(whats_this)

    def get(self) -> float:
        """
        Get the float value stored in the box
        :return: the float value given by the user
        """
        return self.value()

    def set(self, value: float):
        """
        Set the value in the box
        :param value: set the float value in the box
        """
        self.setValue(value)


class NewFileDialog(QDialog):
    def __init__(self, base_path):
        super(self.__class__, self).__init__()

        self.date = None        # will fill once Okay is hit

        self.formGroupBox = QGroupBox("Enter measurement details for the dataset")

        self.bridge_box = DropDown(choices=["Andeen-Hagerling 2500A", "Hewlett Packard 4275", "Fake"],
                                   shortcuts=["AH", "HP", "FAKE"],
                                   label="Capacitance Bridge",
                                   whats_this="What capacitance bridge model are you interacting with?")
        self.ls_box = DropDown(choices=["LS331", "LS340"],
                               shortcuts=[331, 340],
                               label="Temperature Controller being used",
                               whats_this="Which Lakeshore Temperature Controller is being used?")
        self.purp_box = DropDown(choices=["Calibration", "Powder Sample", "Thin Film", "Other", "Test"],
                                 shortcuts=["CAL", "POW", "FILM", "OTHER", "TEST"],
                                 label="")

class NewFileDialog2(QDialog):
    def __init__(self, base_path):
        super(NewFileDialog, self).__init__()
        # self.set
        # self.setGeometry(50, 100, 800, QSizePolicy.Maximum)

        self.date = None        # will fill in once Okay is pressed

        self.formGroupBox = QGroupBox("Enter Measurement Details")
        self.bridgeChoices = QComboBox()
        self.cryoChoices = QComboBox()
        self.purpChoices = QComboBox()
        self.chipIDEntry = QLineEdit()
        self.sampleEntry = QLineEdit()
        self.freqEntry = QLineEdit()
        self.calButton = QPushButton()
        self.filmThickEntry = QLineEdit()
        self.voltEntry = QLineEdit()
        self.aveSetting = QSpinBox()
        self.dcBiasChoice = QComboBox()
        self.dcBiasEntry = QLineEdit()
        self.ampEntry = QLineEdit()
        self.ljEntry0 = QLineEdit()
        self.ljEntry1 = QLineEdit()
        self.ljEntry2 = QLineEdit()
        self.ljEntry3 = QLineEdit()

        self.setWindowIcon(custom_icon('app.png'))

        self.base_path = base_path
        self.cal_path = os.path.join(base_path, '1-Calibrations')
        """LOAD PRESETS"""
        yaml_fname = max(glob.glob(os.path.join(self.base_path, 'presets', '*yml')), key=datetime_from_yaml_name)
        yaml_f = os.path.join(self.base_path, 'presets', yaml_fname)
        print(yaml_f)
        with open(yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        self.bridge_choice = preset['bridge']
        self.cryo_choice = preset['ls']
        self.purp_choice = preset['purp']
        self.chipID_entry = preset['id']
        self.sample_entry = preset['sample']
        self.freq_entry = preset['freqs']
        self.cal_entry = preset['cal']
        self.thick_entry = preset['filmT']
        self.volt_entry = preset['v']
        self.ave_entry = preset['ave']
        self.dcBias_choice = preset['dc']
        self.dcBias_entry = preset['dcv']
        self.amp_entry = preset['amp']
        self.lj_entry = preset['lj']
        self.comment_entry = preset['comment']

        self.createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept_click)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Measurement Details")

    def createFormGroupBox(self):
        layout = QFormLayout()

        """Select Bridge being used"""
        self.bridgeChoices.addItems(["Andeen-Hagerling 2500A", "HP 4275A", "Fake Bridge"])
        bridge_setting = {'ah': 0, 'hp': 1, 'fake': 2}
        self.bridgeChoices.setCurrentIndex(bridge_setting[self.bridge_choice])

        """Select Cryostat Being Used"""
        cryo_choices = ["LS331", "LS340"]
        self.cryoChoices.addItems(cryo_choices)
        cryo_setting = {"LS331": 331, "LS340": 340}
        self.cryoChoices.setCurrentIndex(cryo_choices.index(self.cryo_choice))

        """Select Purpose of Measurement"""
        purp_choices = ["Calibration", "Powder Sample", "Film Sample", "Other"]
        self.purpChoices.addItems(purp_choices)
        purp_setting = {'cal': 0, 'powder': 1, 'film': 2, 'other': 3}
        self.purpChoices.setCurrentIndex(purp_choices.index(self.purp_choice))

        """Specify Chip iD"""
        self.chipIDEntry.setText(self.chipID_entry)

        """Specify Sample"""
        self.sampleEntry.setText(self.sample_entry)

        """Specify Frequencies"""
        self.freqEntry.setText(str(self.freq_entry).strip('[').strip(']'))

        """Calibration File"""
        self.calButton.clicked.connect(self.findCal)
        self.calButton.setText(self.cal_entry)

        """Film Thickness"""
        self.filmThickEntry.setText(str(self.thick_entry))

        """Measurement Voltage"""
        self.voltEntry.setText(str(self.volt_entry))

        """Averaging"""
        self.aveSetting.setValue(int(self.ave_entry))

        """DC Bias Setting"""
        self.dcBiasChoice.addItems(["Off", "I-Low", "I-High"])
        dc_setting = {'off': 0, 'low': 1, 'high': 2}
        self.dcBiasChoice.setCurrentIndex(dc_setting[self.dcBias_choice])

        """DC Bias Value"""
        self.dcBiasEntry.setText(str(self.dcBias_entry))

        """Amplifier"""
        self.ampEntry.setText(str(self.amp_entry))

        """Labjack Channels"""
        self.ljEntry0.setText(self.lj_entry[0])
        self.ljEntry1.setText(self.lj_entry[1])
        self.ljEntry2.setText(self.lj_entry[2])
        self.ljEntry3.setText(self.lj_entry[3])

        """Comments"""
        self.commentEntry = QLineEdit()
        self.commentEntry.setText(self.comment_entry)

        labels = [QLabel("Bridge:"),
                  QLabel("Cryostat:"),
                  QLabel("Purpose:"),
                  QLabel("Chip iD:"),
                  QLabel("Sample:"),
                  QLabel("Frequencies [Hz]:"),
                  QLabel("Use Calibration:"),
                  QLabel("Film Thickness [\u0b3cm]:"),
                  QLabel("Measurement Voltage [V]:"),
                  QLabel("Averaging Setting:"),
                  QLabel("DC Bias Setting:"),
                  QLabel("DC Bias Value [V]"),
                  QLabel("Amplification"),
                  QLabel("Labjack CH0:"),
                  QLabel("Labjack CH1:"),
                  QLabel("Labjack CH2:"),
                  QLabel("Labjack CH3:"),
                  QLabel("Comments:")]
        choices = [self.bridgeChoices, self.cryoChoices, self.purpChoices, self.chipIDEntry, self.sampleEntry,
                   self.freqEntry, self.calButton, self.filmThickEntry, self.voltEntry, self.aveSetting,
                   self.dcBiasChoice, self.dcBiasEntry, self.ampEntry, self.ljEntry0, self.ljEntry1, self.ljEntry2,
                   self.ljEntry3, self.commentEntry]
        whats = ["Capacitive bridge being used for primary measurement",
                 "Cryostat being used so the code knows which Lakeshore to import",
                 "Will this measurement be used as a calibration of a bare capacitor, or to measure a poweder or film?",
                 "The name of the capacitor",
                 "If calibrating, what is the substrate; if measuring a powder or film, what is it?",
                 "What frequencies would you like to measure at [Hz]? separate by commas",
                 "Click to open prompt to find csv file used to calibrate. Open the dialog and click cancel to clear",
                 "Thickness of the film grown in \u0b3cm.",
                 "The voltage the bridge will use to measure. AH: VRMS, HP: V",
                 "AH: a value from 0 to 15 which will set the averaging amount; HP: number of averages",
                 "This only works with the AH; I-low uses a 100 M\u03A9 resistor; I-high uses a 1 M\u03A9 resistor",
                 "The voltage you would like applied as a DC offset for the measurement in volts",
                 "If using an amplifier to get desired DC offset voltage, what is the amplification amount?",
                 "If using LabJack Channel 0, what is the label? (leave blank if not using)",
                 "If using LabJack Channel 1, what is the label? (leave blank if not using)",
                 "If using LabJack Channel 2, what is the label? (leave blank if not using)",
                 "If using LabJack Channel 3, what is the label? (leave blank if not using)",
                 "Any additional information you'd like saved to the file."]

        for label, choice, what in zip(labels, choices, whats):
            label.setWhatsThis(what)
            layout.addRow(label, choice)

        self.formGroupBox.setLayout(layout)

    @Slot()
    def findCal(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Find Calibration", self.cal_path,
                                                      "CSV (*.csv);;All Files (*)", options=options)
        self.calButton.setText(fileName[fileName.find('1-Calibrations')+len('1-Calibrations'):])

    def accept_click(self):
        self.date = datetime.datetime.fromtimestamp(time.time())
        if self.bridgeChoices.currentIndex() == 0:
            self.bridge_choice = 'ah'
        elif self.bridgeChoices.currentIndex() == 1:
            self.bridge_choice = 'hp'
        elif self.bridgeChoices.currentIndex() == 2:
            self.bridge_choice = 'fake'

        if self.cryoChoices.currentIndex() == 0:
            self.cryo_choice = 'Desert-LN'
        elif self.cryoChoices.currentIndex() == 1:
            self.cryo_choice = 'Desert-He'
        elif self.cryoChoices.currentIndex() == 2:
            self.cryo_choice = '40K'
        elif self.cryoChoices.currentIndex() == 3:
            self.cryo_choice = '4K'
        elif self.cryoChoices.currentIndex() == 4:
            self.cryo_choice = 'fake'

        if self.purpChoices.currentIndex() == 0:
            self.purp_choice = 'cal'
        elif self.purpChoices.currentIndex() == 1:
            self.purp_choice = 'powder'
        elif self.purpChoices.currentIndex() == 2:
            self.purp_choice = 'film'
        else:
            self.purp_choice = 'other'

        self.chipID_entry = self.chipIDEntry.text()
        self.sample_entry = self.sampleEntry.text()

        unsorted_freq_entry = [float(freq) for freq in self.freqEntry.text().split(',')]
        self.freq_entry = sorted(unsorted_freq_entry)[::-1]
        if len(self.freq_entry) == 0:
            raise IOError('Invalid frequency input')

        self.cal_entry = self.calButton.text()
        self.thick_entry = float(self.filmThickEntry.text())

        self.volt_entry = float(self.voltEntry.text())
        if self.volt_entry > 15.:
            self.volt_entry = 15.

        self.ave_entry = int(self.aveSetting.text())

        if self.dcBiasChoice.currentIndex() == 0:
            self.dcBias_choice = 'off'
        elif self.dcBiasChoice.currentIndex() == 1:
            self.dcBias_choice = 'low'
        else:
            self.dcBias_choice = 'high'
        self.dcBias_entry = float(self.dcBiasEntry.text())
        self.amp_entry = float(self.ampEntry.text())
        self.lj_entry = [self.ljEntry0.text(), self.ljEntry1.text(), self.ljEntry2.text(), self.ljEntry3.text()]
        self.comment_entry = self.commentEntry.text()

        presets = {'inst': self.bridge_choice,
                   'cryo': self.cryo_choice,
                   'purp': self.purp_choice,
                   'id': self.chipID_entry,
                   'sample': self.sample_entry,
                   'freqs': self.freq_entry,
                   'cal': self.cal_entry,
                   'filmT': self.thick_entry,
                   'v': self.volt_entry,
                   'ave': self.ave_entry,
                   'dc': self.dcBias_choice,
                   'dcv': self.dcBias_entry,
                   'amp': self.amp_entry,
                   'lj': self.lj_entry,
                   'comment': self.comment_entry}

        save_name = f'presets{self.date.year:04}-{self.date.month:02}-{self.date.day:02}_{self.date.hour:02}.yml'
        save_presets = os.path.join(self.base_path, 'presets', save_name)
        with open(save_presets, 'w') as f:
            yaml.dump(presets, f, default_flow_style=False)

        self.cal_entry = os.path.join(self.cal_path, self.cal_entry)

        self.accept()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import get
    app = QApplication(sys.argv)
    dialog = NewFileDialog(os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy-2'))
    sys.exit(dialog.exec())
