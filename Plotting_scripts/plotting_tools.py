import itertools
import csv
import operator
import numpy as np


def most_common(L):
    """Returns the value found most common in a list"""
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item

    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def get_labels(f):
    """Retrieve data file's comment"""
    with open(f[0], 'r') as fff:
        labels = next(itertools.islice(csv.reader(fff), 2, None))
    return labels


def get_f_labels(f):
    global labels
    f_labels = [''] * 3
    ii = 0
    # print 'it is here'
    for label in labels:
        # print(label)
        if 'Frequency' in label:
            label_list = label.strip(' ').split(' ')
            print(label_list)
            for ll in label_list:
                # print(ll)
                if 'Hz' in ll and ll.strip('[').strip(']') == ll:
                    # print(ll)
                    f_labels[ii] = ll.strip('(').strip(')')
                    ii += 1
    # print('\n', f_labels, '\n')
    return f_labels


def load_data(files_to_use):
    skip = 0
    temp_skip = -1
    while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
        temp_skip = skip
        try:
            data = np.loadtxt(files_to_use[0], comments='#', delimiter=',', skiprows=3)
        except StopIteration:
            skip += 1
    if len(files_to_use) > 1:
        for ii, f in enumerate(files_to_use[1:]):
            try:
                data_temp = np.loadtxt(f, comments='#', delimiter=',', skiprows=3)
                try:
                    data = np.append(data, data_temp, axis=0)
                except ValueError:
                    data = np.append(data, np.array([data_temp]), axis=0)
            except StopIteration:
                pass
    return data