from GPIB import GPIB_unix

"""Driver for using HP Waveform Generator"""


class dev(GPIB_unix):  # inherit basic commands from general_instrument_control.py
    def __init__(self, addr, serialport=''):
        """Connect to temperature controller and initialize communication"""
        self.addr = addr
        self.port = serialport

    def id(self):
        """Get identity of device"""
        return self.write('*IDN?')

    def set_waveform(self, frequency, voltage_range, shape='SIN', amp=False):
        """Set frequency and voltage range for waveform"""
        """frequency in kHz, voltage range [v1,v2] in volts"""
        """SIN, SQU, TRI, RAMP"""
        if type(voltage_range) != list:
            voltage_range = [voltage_range]
        if len(voltage_range) == 1:
            voltage_range = [-voltage_range[0], voltage_range[0]]
        if len(voltage_range) > 2:
            raise IOError('Voltage range should be a list of no more than 2 values')
        shape = shape.upper()
        if shape not in ['SIN', 'SQU', 'TRI', 'RAMP']:
            raise IOError('Shape not valid')
        if amp:
            voltage_range /= 50.
        voltage_range.sort()
        dc_offset = sum(voltage_range) / len(voltage_range)
        pp_volt = voltage_range[1] - voltage_range[0]
        msg = 'APPL:SIN %.1fE+3, %.1f, %.1f' % (frequency, pp_volt, dc_offset)
        self.write2(msg)

    def set_dc(self, voltage):
        msg = 'APPL: '


if __name__ == '__main__':
    import get

    bridge = dev(13, get.serialport())
