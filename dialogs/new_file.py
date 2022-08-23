import PyQt5.QtWidgets as qtw
import sys
import yaml
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
import os
import glob
import datetime
import time


class StartMeasDialog(qtw.QDialog):
    def __init__(self, base_path):
        super(StartMeasDialog, self).__init__()
        self.setGeometry(50, 100, 800, qtw.QSizePolicy.Maximum)

        self.date = None        # will fill in once Okay is pressed

        self.formGroupBox = qtw.QGroupBox("Enter Measurement Details")
        self.bridgeChoices = qtw.QComboBox()
        self.cryoChoices = qtw.QComboBox()
        self.purpChoices = qtw.QComboBox()
        self.chipIDEntry = qtw.QLineEdit()
        self.sampleEntry = qtw.QLineEdit()
        self.freqEntry = qtw.QLineEdit()
        self.calButton = qtw.QPushButton()
        self.filmThickEntry = qtw.QLineEdit()
        self.voltEntry = qtw.QLineEdit()
        self.aveSetting = qtw.QSpinBox()
        self.dcBiasChoice = qtw.QComboBox()
        self.dcBiasEntry = qtw.QLineEdit()
        self.ampEntry = qtw.QLineEdit()
        self.ljEntry0 = qtw.QLineEdit()
        self.ljEntry1 = qtw.QLineEdit()
        self.ljEntry2 = qtw.QLineEdit()
        self.ljEntry3 = qtw.QLineEdit()

        self.setWindowIcon(QIcon(os.path.join('custom_icons', 'app.png')))

        self.base_path = base_path
        self.cal_path = os.path.join(base_path, '1-Calibrations')
        """LOAD PRESETS"""
        yaml_fname = max(glob.glob(os.path.join(self.base_path, 'presets', '*yml')), key=os.path.getctime)
        yaml_f = os.path.join(self.base_path, 'presets', yaml_fname)
        print(yaml_f)
        with open(yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        self.bridge_choice = preset['inst']
        self.cryo_choice = preset['cryo']
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

        buttonBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept_click)
        buttonBox.rejected.connect(self.reject)

        mainLayout = qtw.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Measurement Details")

    def createFormGroupBox(self):
        layout = qtw.QFormLayout()

        """Select Bridge being used"""
        self.bridgeChoices.addItems(["Andeen-Hagerling 2500A", "HP 4275A", "Fake Bridge"])
        bridge_setting = {'ah': 0, 'hp': 1, 'fake': 2}
        self.bridgeChoices.setCurrentIndex(bridge_setting[self.bridge_choice])

        """Select Cryostat Being Used"""
        self.cryoChoices.addItems(["DesertCryo-LN", "DesertCryo-He", "Frankenstein", "Dan's", "Fake Cryo"])
        cryo_setting = {'Desert-LN': 0, 'Desert-He': 1, '40K': 2, '4K': 3, 'fake': 4}
        self.cryoChoices.setCurrentIndex(cryo_setting[self.cryo_choice])

        """Select Purpose of Measurement"""
        self.purpChoices.addItems(["Calibration", "Powder Sample", "Film Sample", "Other"])
        purp_setting = {'cal': 0, 'powder': 1, 'film': 2, 'other': 3}
        self.purpChoices.setCurrentIndex(purp_setting[self.purp_choice])

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
        self.commentEntry = qtw.QLineEdit()
        self.commentEntry.setText(self.comment_entry)

        labels = [qtw.QLabel("Bridge:"),
                  qtw.QLabel("Cryostat:"),
                  qtw.QLabel("Purpose:"),
                  qtw.QLabel("Chip iD:"),
                  qtw.QLabel("Sample:"),
                  qtw.QLabel("Frequencies [Hz]:"),
                  qtw.QLabel("Use Calibration:"),
                  qtw.QLabel("Film Thickness [\u0b3cm]:"),
                  qtw.QLabel("Measurement Voltage [V]:"),
                  qtw.QLabel("Averaging Setting:"),
                  qtw.QLabel("DC Bias Setting:"),
                  qtw.QLabel("DC Bias Value [V]"),
                  qtw.QLabel("Amplification"),
                  qtw.QLabel("Labjack CH0:"),
                  qtw.QLabel("Labjack CH1:"),
                  qtw.QLabel("Labjack CH2:"),
                  qtw.QLabel("Labjack CH3:"),
                  qtw.QLabel("Comments:")]
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

    @pyqtSlot()
    def findCal(self):
        options = qtw.QFileDialog.Options()
        options |= qtw.QFileDialog.DontUseNativeDialog
        fileName, _ = qtw.QFileDialog.getOpenFileName(self, "Find Calibration", self.cal_path,
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
    import get
    app = qtw.QApplication(sys.argv)
    dialog = StartMeasDialog(os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy-2'))
    sys.exit(dialog.exec_())
