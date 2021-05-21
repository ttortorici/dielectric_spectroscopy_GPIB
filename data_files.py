import time

from client_tools import *
from calculations import geometric_capacitance


class DataFile:

    cryo_to_ls = {'DESERT-LN': 340, 'DESERT-HE': 340, '40K': 331, '4K': None}

    def __init__(self, path, filename, port, unique_freqs, bridge='AH', cryo='40K', comment='', lj_chs=[]):
        """Create data file, and instances of the bridge and Lakeshore for communication"""
        self.name = os.path.join(path, filename)
        print(unique_freqs)
        list.sort(unique_freqs)
        self.unique_freqs = unique_freqs[::-1]
        if '.csv' not in self.name:
            self.name += '.csv'  # if there's no .csv, append it on the end
        self.write_row("# This data file was created on {}".format(time.ctime(time.time())))
        self.write_row('# {}'.format(comment))

        if bridge.upper()[0:2] == 'AH':
            self.bridge = AH2700A(port)
        elif bridge.upper()[0:2] == 'HP':
            self.bridge = HP4275A(port)
        self.cryo = cryo.upper()
        self.ls = LakeShore(port, self.cryo_to_ls[self.cryo])

        self.lj_chs = lj_chs
        if len(lj_chs) > 0:
            self.lj = LabJack.LabJack()
            print('imported LabJack')
        else:
            self.lj = None
            print('did not import LabJack')
        self.labels = []
        self.labels_to_write = []
        self.set_labels()
        self.write_labels()
        self.start_time = time.time()

    def set_labels(self):
        """Exclude LabJack (for now) and frequency"""
        self.labels = ['Time [s]']
        if self.cryo == '40K':
            self.labels.append('Temperature [K]')
        else:
            self.labels.extend(['A Temperature [K]', 'B Temperature [K]'])
        self.labels.extend(['Capacitance [pF]', 'Loss Tangent', 'Voltage [V]'])

    def write_labels(self):
        for freq in self.unique_freqs:
            f = str(int(freq))
            if len(f) <= 3:
                f += 'Hz'
            elif len(f) <= 6:
                f = f[:-3] + 'kHz'
            elif len(f) <= 9:
                f = f[:-6] + 'MHz'
            elif len(f) <= 12:
                f = f[:-9] + 'GHz'
            for label in self.labels:
                self.labels_to_write.append('{} ({})'.format(label, f))
            if type(self.lj_chs) == list:
                for ii, ch in enumerate(self.lj_chs):
                    self.labels.extend(['LJ {} [V] ({})'.format(ch, f), 'LJ StdDev {} [V] ({})'.format(ch, f)])
            self.labels.append('Frequency [Hz]')
            self.write_row(self.labels_to_write)

    def sweep_freq(self, amp=1, offset=0):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        data_to_write = []
        for ii, freq in enumerate(self.unique_freqs):
            self.bridge.set_freq(freq)
            print('frequency set')

            if self.bridge.abbr == 'HP':
                time.sleep(1)
            bridge_data = self.bridge.read_front_panel()
            while bridge_data[-1] == -1:
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
            data_f.extend(bridge_data[1:])

            """Write LabJack Data if using it"""
            if type(self.lj_chs) == list:
                if len(self.lj_chs) > 0:
                    lj_val, lj_err = list(np.array(list(chain(*self.lj.read_voltages_ave(self.lj_chs)))) * amp)
                    data_f.extend([lj_val + offset, lj_err])

            """Write frequency measured at"""
            data_f.append(bridge_data[0])

            print(data_f)
            data_to_write.extend(data_f)
        self.write_row(data_to_write)

    def write_row(self, row_to_write):
        with open(self.name, 'a') as f:
            f.write(str(row_to_write).strip('[').strip(']').replace("'", "") + '\n')


class CalFile(DataFile):
    pass


class DielectricConstant(DataFile):
    """path [str] - file path to where you want to write the file
       filename [str] - name of the file to write
       port [int] - port number to communicate with GPIB comm server
       unique_freqs [list of int or float] - frequencies to measure
       filmThicknes [float] - thickness of the film in [um]
       gapWidth [float] - distance between fingers in [um]
       bareFit [list] - with [0]: [c0, c1, c2] for capacitance and [1]: [a0, a1] for loss"""
    def __init__(self, path, filename, port, uniqueFreqs, filmThickness, gapWidth, bareCFit, bareDFit,
                 bridge='AH', cryo='40K', comment='', lj_chs=[]):
        super(self.__class__, self).__init__(path, filename, port, uniqueFreqs, bridge, cryo, comment, lj_chs)

        self.cGeo = geometric_capacitance(gapWidth, filmThickness)

        self.bareFitC = bareCFit
        self.bareFitD = bareDFit

    def set_labels(self):
        """Exclude LabJack (for now) and frequency"""
        self.labels = ['Time [s]']
        if self.cryo == '40K':
            self.labels.append('Temperature [K]')
        else:
            self.labels.extend(['A Temperature [K]', 'B Temperature [K]'])
        self.labels.extend(['Capacitance [pF]', 'Loss Tangent', 'Re eps', 'Im eps'])

    def sweep_freq(self, amp=1, offset=0):
        """Sweep a set of frequencies"""
        print('Starting frequency sweep measurements')
        data_to_write = []
        for ii, freq in enumerate(self.unique_freqs):
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
            for ii, c in enumerate(self.bareFitC):
                cBare += c[ii]*temperatures[0]**ii
            lBare = 0
            for ii, c in enumerate(self.bareFitD):
                lBare += c[ii]*temperatures[0]**ii

            reEps = 1 + (bridge_data[1] - cBare) / self.cGeo
            imEps = (bridge_data[2] * bridge_data[1] - lBare * cBare) / self.cGeo

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
        self.write_row(data_to_write)
