"""
classes for communicating with Lakeshore temperature controllers

@author: Teddy Tortorici
"""

import numpy as np
from comm.socket_client import Device


class Client(Device):
    def __init__(self, model_num: int):
        """
        Objects will send commands to the socket server to handle GPIB commands
        :param model_num: lakeshore model number
        """
        super(self.__class__, self).__init__("LS")
        self.inst_num = model_num

        # create list of heater range values in Watts
        # The index is the setting value on the instrument
        # The element corresponding to that index is the power in Watts
        if model_num == 340:
            self.heater_ranges = np.array([0.0, 0.05, 0.5, 5.0, 50.0])
        else:
            self.heater_ranges = np.array([0.0, 0.5, 5.0, 50.0])
        # Get PID values set on channel 1 and 2. the 0th entry is a dummy, since the loops index from 1
        self.PID = [0, self.read_pid(1), self.read_pid(2)]

    def read_front_panel(self, units: str = 'K') -> list[float]:
        """
        Read temperature from both stages
        :param units: K or C
        :return: [Stage A, Stage B] temperatures
        """
        units = units.upper()
        if units not in ['K', 'C']:
            raise ValueError('Must give units "K" or "C"')

        temperature_a = float(self.query('{}RDG? A'.format(units)))
        temperature_b = float(self.query('{}RDG? B'.format(units)))
        return [temperature_a, temperature_b]

    def read_heater_output(self) -> float:
        """Query the percent power being output to the heater"""
        return float(self.query('HTR?'))

    def read_heater_range(self) -> float:
        """Query the heater range. Returns value in Watts"""
        return float(self.heater_ranges[int(self.query('RANGE?'))])

    def read_pid(self, loop: int = 1) -> tuple:
        """Returns in units of Kelvin per minute"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        msg_back = self.query(f"PID? {int(loop)}")
        pid = [float(element) for element in msg_back.split(',')]
        return tuple(pid)

    def read_ramp_speed(self, loop: int = 1) -> float:
        """Kelvin per minute"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        return float(self.query(f"RAMP? {loop}").split(',')[1])

    def read_ramp_status(self, loop: int = 1) -> bool:
        """Check whether the setpoint is ramping or not"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        return bool(int(self.query(f"RAMPST? {loop}")))

    def read_setpoint(self, loop=1):
        """Return the value of setpoint in current units"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        return float(self.query(f"SETP? {loop}"))

    def read_temperature(self, channel: str = 'A', units: str = 'K') -> float:
        """Read the temperature on a channel"""
        # Ensure the variables are uppercase
        channel = channel.upper()
        units = units.upper()

        # Ensure the variables are valid
        if channel not in ['A', 'B']:
            raise IOError(f"Invalid channel: {channel}")
        if units not in ['K', 'C']:
            raise IOError(f"Invalid units: {units}")
        return float(self.query(f"{units}RDG? {channel}"))

    def set_heater_range(self, power_range: float, override: bool = False):
        """Sets the heater range"""
        # ensure that the power_range is positive
        power_range = abs(float(power_range))

        # find the nearest valid setting to the power given
        setting = np.argmin(self.heater_ranges - power_range)
        if self.heater_ranges[setting] == 50. and not override:
            print("50V is probably too high and will fry your solder joints. If you disagree, override==True")
        else:
            self.write(f"RANGE {setting}")

    def set_pid(self, p='', i='', d='', loop=1):
        """Sets PID control values on loop 1 or 2"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        if p == '':
            p = self.PID[loop][0]
        else:
            self.PID[loop][1] = float(p)
        if i == '':
            i = self.PID[loop][1]
        else:
            self.PID[loop][1] = float(i)
        if d == '':
            d = self.PID[loop][2]
        else:
            self.PID[loop][2] = float(d)
        self.write(f"PID {loop}, {p}, {i}, {d}")

    def set_ramp_speed(self, kelvin_per_min, loop=1):
        """Set the ramp speed to reach set point in Kelvin per min"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        self.write(f"RAMP {loop}, 1, {kelvin_per_min}")

    def set_setpoint(self, value, loop=1):
        """Configure Control loop setpoint.
        loop: specifies which loop to configure.
        value: the value for the setpoint (in whatever units the setpoint is using"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        self.write(f"SETP {loop}, {float(value)}")
