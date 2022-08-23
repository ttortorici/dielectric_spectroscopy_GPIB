"""
Classes for creating and managing data files

@author: Teddy Tortorici
"""

import time
import os
import numpy as np
from devices.ah2700 import Client as BridgeAH
from devices.hp4275 import Client as BridgeHP
from devices.lakeshore import Client as Lakeshore
from calculations import geometric_capacitance


class CSVFile:

    file_type = ".csv"

    def __init__(self, path: str, filename: str, comment: str = ""):
        """
        Create or open a csv file and manage it.
        :param path: file path to where you want to save the file
        :param name: name of the file you wish to create or open
        :param comment: an optional comment to put in the file
        """

        """MAKE SURE THE FILE NAME IS VALID"""
        filename = filename.rstrip(CSVFile.file_type)
        filename = filename.replace(".", "")
        filename += CSVFile.file_type
        self.name = os.path.join(path, filename)

        """CHECK IF PATH TO FILE AND FILE EXIST"""
        # Check if path exists, if it doesn't, make all the directories necessary to make it
        if not os.path.isdir(path):
            os.makedirs(path)

        # Check if file exists, if it doesn't, make it
        if os.path.exists(self.name):
            self.new = False
        else:
            self.new = True
            self.create_file()

        """APPEND OPTIONAL COMMENT"""
        if comment:
            self.write_comment(comment)

    def write_row(self, row_to_write: list):
        """Turns a list into a comma delimited row to write to the csv file"""
        with open(self.name, 'a') as f:
            f.write(str(row_to_write).lstrip("[").rstrip("]") + '\n')

    def write_comment(self, comment: str):
        """Writes a comment line in the csv file"""
        with open(self.name, "a") as f:
            f.write(f"# {comment}\n")

    def create_file(self):
        """Creates file by writing the first comment line"""
        with open(self.name, "w") as f:
            f.write(f"# This data file was created on {time.ctime(time.time())}\n")


class DataFile(CSVFile):

    cryo_to_ls = {'DESERT-LN': 340, 'DESERT-HE': 340, '40K': 331, '4K': None, 'FAKE': 331}
    labels = ('Time [s]', 'Temperature A [K]', 'Temperature B [K]',
              'Capacitance [pF]', 'Loss Tangent', 'Voltage [V]', 'Frequency [Hz]')

    def __init__(self, path: str, filename: str, frequencies: list,
                 bridge: str = 'AH', cryo: str = '40K', comment: str = "", lj_chs: list = None):
        """
        Create data file, and instances of the Bridge and Lakeshore for communication
        :param path: path you want to save the file
        :param filename: name of the file
        :param frequencies: list of ints. frequencies to measure at. Will remove duplicates and reverse sort them
                            so measurements are made from the highest frequency to the lowest frequency.
        :param bridge: "AH" or "HP" to select which bridge to use.
        :param cryo: Which cryostat you're using.
        :param comment: Will write the comment after opening the file with the # header so that is ignored.
        :param lj_chs: Not currently supported.
        """
        super(self.__class__, self).__init__(path, filename, comment)
        unique_frequencies = list(set(frequencies))         # remove repeated entries
        unique_frequencies.sort()                           # sort the list
        self.unique_frequencies = unique_frequencies[::-1]  # reverse order (big to small)

        if bridge.upper()[0:2] == 'AH' or bridge == 'fake':
            self.bridge = BridgeAH()
        elif bridge.upper()[0:2] == 'HP':
            self.bridge = BridgeHP()
        self.cryo = cryo.upper()
        self.ls = Lakeshore(self.cryo_to_ls[self.cryo])

        self.lj_chs = lj_chs
        # if len(lj_chs) > 0:
        #     self.lj = LabJack.LabJack()
        #     print('imported LabJack')
        # else:
        #     self.lj = None
        #     print('did not import LabJack')

        self.labels = [""] * len(self.__class__.labels) * len(self.unique_frequencies)
        if self.new:
            self.write_labels()
        self.start_time = time.time()

    def write_labels(self):
        """
        Uses DataFile.labels to construct labels for each individual measurement frequency and then writes them to the
        data file
        """
        for ff, frequency in enumerate(self.unique_frequencies):
            if frequency < 1e3:
                f_label = f"{int(frequency):d} Hz"
            elif frequency < 1e6:
                f_label = f"{int(frequency / 1e3):d} kHz"
            elif frequency < 1e9:
                f_label = f"{int(frequency / 1e6):d} MHz"
            elif frequency < 1e12:
                f_label = f"{int(frequency / 1e9):d} GHz"
            elif frequency < 1e15:
                f_label = f"{int(frequency / 1e12):d} THz"
            else:
                f_label = f"{int(frequency / 1e15):d} PHz"
            for ll, label in enumerate(self.__class__.labels):
                self.labels[ff + ll] = f"{label:s} ({f_label:s})"
            # if type(self.lj_chs) == list:
            #     for ii, ch in enumerate(self.lj_chs):
            #         self.labels.extend(['LJ {} [V] ({})'.format(ch, f), 'LJ StdDev {} [V] ({})'.format(ch, f)])
        self.write_row(self.labels)

    def measure_at_frequency(self, frequency: int, attempts: int = 3, silent: bool = True):  # , amp=1, offset=0):
        """
        Just measure at one frequency
        :param frequency: The frequency to measure at in Hz
        :param attempts: how many times to attempt to get data after failed attempts
        :param silent: if silent, then it doesn't print anything
        """
        if not silent:
            print('Starting measurement')

        data = [0] * len(self.__class__.labels)

        """Set the frequency"""
        self.bridge.set_freq(frequency)

        if not silent:
            print(f'Frequency set to {frequency} Hz')

        if self.bridge.dev_id == 'HP':
            time.sleep(1)

        """Make attempts to read from the bridge"""
        for _ in range(attempts):
            bridge_data = self.bridge.read_front_panel()
            if bridge_data[-1] != -1:
                break

        if not silent:
            print('read front panel')

        """Read temperatures from lakeshore"""
        temperatures = self.ls.read_front_panel()

        if not silent:
            print('read temperatures')

        data[0] = time.time()
        data[1:3] = temperatures
        data[3:6] = bridge_data[1:]     # capacitance, loss, voltage
        data[6] = bridge_data[0]        # frequency

        return data

    def sweep_freq(self):  # , amp=1, offset=0):
        """
        Repeat measurements at each frequency in self.unique_frequencies
        """
        full_data = [0] * len(self.__class__.labels) * len(self.unique_frequencies)
        for ff, frequency in enumerate(self.unique_frequencies):
            start_index = ff * len(self.__class__.labels)
            end_index = (ff + 1) * len(self.__class__.labels)
            partial_data = self.measure_at_frequency(frequency)
            full_data[start_index:end_index] = partial_data
        self.write_row(full_data)
        return full_data


class CalFile(DataFile):
    def __init__(self, path: str, filename: str, frequencies: list,
                 bridge: str = 'AH', cryo: str = '40K', comment: str = "", lj_chs: list = None):
        """
        Calibration files are generically the same as the DataFile class.
        :param path: path you want to save the file
        :param filename: name of the file
        :param frequencies: list of ints. frequencies to measure at. Will remove duplicates and reverse sort them
                            so measurements are made from the highest frequency to the lowest frequency.
        :param bridge: "AH" or "HP" to select which bridge to use.
        :param cryo: Which cryostat you're using.
        :param comment: Will write the comment after opening the file with the # header so that is ignored.
        :param lj_chs: Not currently supported.
        """
        super(self.__class__, self).__init__(path, filename, frequencies, bridge, cryo, comment, lj_chs)


class DielectricConstant(DataFile):

    labels = ('Time [s]', 'Temperature A [K]', 'Temperature B [K]',
              'Capacitance [pF]', 'Loss Tangent', 'Voltage [V]',
              'Re[dielectric constant]', 'Im[dielectric constant]', 'Frequency [Hz]')

    def __init__(self, path: str, filename: str, frequencies: list,
                 film_thickness: float, gap_width: float, bare_cap_fit: list, bare_loss_fit: list,
                 bridge: str = 'AH', cryo: str = '40K', comment: str = "", lj_chs: list = None):
        """
        Data file for measuring a well characterized sample after calibrating the bare capacitor
        :param path: file path where you want to write the file
        :param filename: name of the file
        :param frequencies: list of int. frequencies to measure at
        :param film_thickness: measured film thickness in [um]
        :param gap_width: distance between interdigital fingers in [um]
        :param bare_cap_fit: [c0, c1, c2, ...] which are fit params for C vs T: sum(c_i * T^i)
        :param bare_loss_fit: [a0, a1, a2, ...] which are fit params for L vs T: sum(a_i * T^i)
        :param bridge: 'AH' or 'HP': Two character string signifying which bridge to use
        :param cryo: string signifying which experimental setup being used
        :param comment: optional comment to append to datafile when started
        :param lj_chs: not supported currently
        """
        super(self.__class__, self).__init__(path, filename, frequencies, bridge, cryo, comment, lj_chs)

        self.geometric_cap = geometric_capacitance(gap_width, film_thickness)

        self.bare_cap_fit = bare_cap_fit
        self.bare_loss_fit = bare_loss_fit

        '''print('Starting frequency sweep measurements')
        data_to_write = []
        for ii, freq in enumerate(self.unique_frequencies):
            self.bridge.set_freq(freq)
            print('frequency set')

            bridge_data = self.bridge.read_front_panel()
            if bridge_data == [-1, -1, -1, -1]:
                bridge_data = self.bridge.read_front_panel()
            print('read front panel')

            temperatures = [self.ls.read_temp('A')]
            if self.cryo != '40K':
                temperatures.append(self.ls.read_temp('B'))
            print('read temperatures')

            """Write time elapsed"""
            data_f = [time.time()-self.start_time]

            """Write Temperatures"""
            for temperature in temperatures:
                data_f.append(temperature)

            """Write data from bridge"""
            data_f.extend(bridge_data[1:-1])

            cBare = 0
            for ii, c in enumerate(self.bare_cap_fit):
                cBare += c[ii]*temperatures[0]**ii
            lBare = 0
            for ii, c in enumerate(self.bare_loss_fit):
                lBare += c[ii]*temperatures[0]**ii

            reEps = 1 + (bridge_data[1] - cBare) / self.geometric_cap
            imEps = (bridge_data[2] * bridge_data[1] - lBare * cBare) / self.geometric_cap

            data_f.extend([reEps, imEps])

            """Write LabJack Data if using it"""
            if type(self.lj_chs) == list:
                if len(self.lj_chs) > 0:
                    lj_val, lj_err = list(np.array(list(chain(*self.lj.read_voltages_ave(self.lj_chs)))) * amp)
                    data_f.extend([lj_val + offset, lj_err])

            """Write frequency measured at"""
            data_f.append(bridge_data[0])

            print(data_f)
            data_to_write.extend(data_f)
        self.write_row(data_to_write)'''
    def measure_at_frequency(self, frequency: int, attempts: int = 3, silent: bool = True):  # , amp=1, offset=0):
        """
        Just measure at one frequency
        :param frequency: The frequency to measure at in Hz
        :param attempts: how many times to attempt to get data after failed attempts
        :param silent: if silent, then it doesn't print anything
        """
        if not silent:
            print('Starting measurement')

        data = [0] * len(self.__class__.labels)

        """Set the frequency"""
        self.bridge.set_freq(frequency)

        if not silent:
            print(f'Frequency set to {frequency} Hz')

        if self.bridge.dev_id == 'HP':
            time.sleep(1)

        """Make attempts to read from the bridge"""
        for _ in range(attempts):
            bridge_data = self.bridge.read_front_panel()
            if bridge_data[-1] != -1:
                break

        if not silent:
            print('read front panel')

        """Read temperatures from lakeshore"""
        temperatures = self.ls.read_front_panel()

        if not silent:
            print('read temperatures')

        data[0] = time.time()
        data[1:3] = temperatures
        data[3:6] = bridge_data[1:]     # capacitance, loss, voltage
        data[6] = bridge_data[0]        # frequency

        return data