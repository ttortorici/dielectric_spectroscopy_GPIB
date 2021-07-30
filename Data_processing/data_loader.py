import numpy as np
import itertools


def load_data(files_to_use):
    data_combined = load(files_to_use)  # returns a single array containing all the data in all the files

    labels = get_labels(files_to_use)   # returns labels for each data column
    frequencies = get_frequencies_used(files_to_use, labels)    # returns

    data_set = DataSet(labels, frequencies, data_combined)

    return data_set


class DataSet:
    def __init__(self, labels, frequency_labels, data_combined):
        self.labels = labels
        self.frequencies = np.zeros(len(frequency_labels))
        for ii, frequency_label in enumerate(frequency_labels):
            if 'mhz' in frequency_label.lower():
                multiplier = 1e6
                units = 'mhz'
            elif 'khz' in frequency_label.lower():
                multiplier = 1e3
                units = 'khz'
            else:
                multiplier = 1.
                units = 'hz'
            self.frequencies[ii] = multiplier * int(frequency_label.strip(units))
        self.stage_num = 1      # number of temperature stages being measured (may be changed to 2 later)

        for label in labels:
            if 'temperature b' in label.lower():
                self.stage_num += 1              # ticks up stage number if a stage B is present
                break

        """Find the column indexes for each data type"""
        time_indexes = [index for index, label in enumerate(labels) if 'time' in label.lower()]
        if len(T_labels) == 1:
            tempA_indexes = [index for index, label in enumerate(labels) if 'temperature' in label.lower()]
            tempB_indexes = None
        else:
            tempA_indexes = [index for index, label in enumerate(labels) if 'temperature a' in label.lower()]
            tempB_indexes = [index for index, label in enumerate(labels) if 'temperature b' in label.lower()]
        cap_indexes = [index for index, label in enumerate(labels) if 'capacitance' in label.lower()]
        loss_indexes = [index for index, label in enumerate(labels) if 'loss' in label.lower()]
        re_eps_index = [index for index, label in enumerate(labels) if 're eps' in label.lower()]
        im_eps_index = [index for index, label in enumerate(labels) if 'im eps' in label.lower()]

        self.timestamps = np.column_stack(([data[:, index] for index in time_indexes]))
        self.temperatureA = np.column_stack(([data[:, index] for index in tempA_indexes]))
        if tempB_indexes:
            self.temperatureB = np.column_stack([data[:, index] for index in tempB_indexes])
        else:
            self.temperatureB = None
        self.capacitances = np.column_stack([data[:, index] for index in cap_indexes])
        self.losses = np.column_stack([data[:, index] for index in loss_indexes])

        if len(re_eps_index) > 0 and len(im_eps_index) > 0:
            self.epsilons = np.column_stack([data[:, index] for index in re_eps_index])
            self.epsilons += 1j * np.column_stack([data[:, index] for index in im_eps_index])
        else:
            self.epsilons = None

    def t(self, frequency):
        return self.timestamps[:, np.where(self.frequencies == frequency)]

    def T(self, frequency):
        return self.temperatureA[:, np.where(self.frequencies == frequency)]

    def TB(self, frequency):
        if self.temperatureB:
            return self.temperatureB[:, np.where(self.frequencies == frequency)]
        else:
            return None

    def C(self, frequency):
        return self.capacitances[:, np.where(self.frequencies == frequency)]

    def loss(self, frequency):
        return self.losses[:, np.where(self.frequencies == frequency)]

    def eps(self, frequency):
        return self.epsilons[:, np.where(self.frequencies == frequency)]

    def epsRe(self, frequency):
        return self.eps(frequency).real

    def epsIm(self, frequency):
        return self.eps(frequency).imag


def load(files_to_load):
    """Load up all the data from a list of files and combine them into a single data array"""
    skip = 0
    temp_skip = -1

    # should get a list, so if given just a single element of a list, turn it into a list
    if isinstance(files_to_load, str):
        files_to_load = [files_to_load]

    while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
        temp_skip = skip
        try:
            data_combined = np.loadtxt(files_to_load[0], comments='#', delimiter=',', skiprows=3)
        except StopIteration:
            skip += 1
    if len(files_to_load) > 1:
        for ii, f in enumerate(files_to_load[1:]):
            try:
                data_temp = np.loadtxt(f, comments='#', delimiter=',', skiprows=3)
                try:
                    data_combined = np.append(data_combined, data_temp, axis=0)
                except ValueError:
                    data_combined = np.append(data_combined, np.array([data_temp]), axis=0)
            except StopIteration:
                pass
    return data_combined


def get_labels(files_being_used):
    """Retrieve data file's column labels"""
    if isinstance(files_being_used, str):
        first_file = files_being_used
    else:
        first_file = files_being_used[0]
    with open(first_file, 'r') as opened_file:
        data_labels = next(itertools.islice(csv.reader(opened_file), 2, None))
    return data_labels


def get_frequencies_used(files_being_used, labels, frequency_num=3):
    """Returns a list of what frequencies are being used
    list of strings with units"""
    frequencies_per_file = [''] * len(files_being_used)
    for ff, file in enumerate(files_being_used):
        frequencies = [''] * frequency_num
        ii = 0
        for label in labels:
            if 'Frequency' in label:
                label_list = label.strip(' ').split(' ')
                print(label_list)
                for ll in label_list:
                    if 'Hz' in ll and ll.strip('[').strip(']') == ll:
                        frequencies[ii] = ll.strip('(').strip(')')
                        ii += 1
        frequencies_per_file[ff] = frequencies

    frequency_labels = most_common(frequencies_per_file)

    return frequency_labels


def most_common(list_to_sift_through):
    """Returns the value found most common in a list"""
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(list_to_sift_through))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item
    def _auxfunction(g):
        item, iterable = g
        count = 0
        min_index = len(list_to_sift_through)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfunction)[0]


if __name__ == '__main__':
    print('I am for importing')
