import socket
import sys
import time
import random
import os


class data_file:
    def __init__(self, path, filename, unique_freqs=None, comment=''):
        """Create data file, and instances of the bridge and lakeshore for communication"""
        self.name = os.path.join(path, filename)
        self.filename = filename.lower()
        list.sort(unique_freqs)
        self.unique_freqs = unique_freqs[::-1]
        if '.csv' not in self.name:
            self.name += '.csv'     # if there's no .csv, append it on the end
        self.write_row2("# This data file was created on %s" % time.ctime(time.time()))
        self.write_row2('# %s' % comment)

        self.bridge = AH2700A.dev(28, get.serialport())
        self.ls = LS340.dev(12, get.serialport())
        try:
            self.lj = LabJack.LabJack()
            print 'imported labjack'
        except:
            self.lj = None
            print 'did not import labjack'
        if self.unique_freqs:
            labels = []
            for freq in self.unique_freqs:
                f = str(int(freq))
                if len(f) < 4:
                    f += 'Hz'
                else:
                    f = f[:-3] + 'kHz'
                labels.extend(['Time %s [s]' % f,
                               'Temperature A %s [K]' % f,
                               'Temperature B %s [K]' % f,
                               'Capacitance %s [pF]' % f,
                               'Loss tangent %s' % f,
                               'Voltage %s [V]' % f])
                if self.lj:
                    for ii in xrange(4):
                        labels.append('DC voltage ch %d %s [V]' % (ii, f))
                labels.append('Frequency %s [Hz]' % f)
            self.write_row2(labels)

        else:
            if 'sorted' in filename.lower():
                self.write_row2(['Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'Frequency [Hz]',
                                 'Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'Frequency [Hz]',
                                 'Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'Frequency [Hz]'
                                 ])
            elif 'dc' in filename.lower():
                self.write_row2(['Time [s]', 'Temperature A [K]', 'Temperature B [K]', 'Frequency [Hz]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]', 'DC Voltage [V]'])
            else:
                self.write_row2(['Time [s]', 'Temperature A [K]', 'Temperature B [K]', 'Frequency [Hz]',
                                 'Capacitance [pF]', 'Loss tangent', 'Voltage [V]'])
        if not win: self.ls.meter.write('++eot_enable')
        #self.bridge.dcbias('hi')

HOST, PORT = "localhost", 9999
data = "init||28"

# Create a socket (SOCK_STREAM means a TCP socket)


while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to server and send data
        print 'entered try'
        sock.connect((HOST, PORT))
        print  'connected'
        sock.sendall(data + "\n")
        
        # Receive data from the server and shut down
        received = sock.recv(1024)
    finally:
        sock.close()

    print "Sent:     {}".format(data)
    print "Received: {}".format(received)
    time.sleep(random.random())