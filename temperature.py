"""
Control the Lakeshore through the GUI
"""

import sys
import numpy as np
import glob
import os
import time
import datetime
import yaml
try:
    import Tkinter
except ImportError:
    import tkinter as Tkinter
import client_tools as tools
import data_files
import get
import csv
import calculations as calc


class Window(Tkinter.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'

    def __init__(self):
        """establish the day data is getting taken
        self.date has attributes .year, .month, .day, .hour, .min, .second, .microsecond"""
        self.date = datetime.datetime.fromtimestamp(time.time())

        # get filepath in google drive
        self.base_path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy-2')

        self.lj_chs = []                    # will be used later
        self.path = self.base_path          # will be added on to later

        # load presets
        yaml_fname = ''
        if len(sys.argv) > 1:
            yaml_fname = str(sys.argv[1]).lower()
        if 'preset' not in yaml_fname:
            yaml_fname = max(glob.glob(os.path.join(self.base_path, 'presets') + '\*yml'), key=os.path.getctime)
        yaml_f = os.path.join(self.base_path, 'presets', yaml_fname)
        with open(yaml_f, 'r') as f:
            preset = yaml.safe_load(f)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('LakeShore GUI')

        """
        create and place labels
        """
        columns = 3

        r = 0

        """TITLE LINE"""
        Tkinter.Label(self, text='Control LakeShore Temperature Controller',
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, columnspan=columns, sticky=Tkinter.W)

        r += 1

        """PORT FOR SERVER COMM"""
        Tkinter.Label(self, text="Port number:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.port = 62535
        self.port_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.port_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.port_entry.insert(0, self.port)

        Tkinter.Button(self, text="SET",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.set_port).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.lj = None
        self.set_port()

        r += 1

        """MODEL NUMBER"""
        Tkinter.Label(self, text="LakeShore Model:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.modl = 331
        self.modl_selection = Tkinter.IntVar(self)

        self.modl_selection.set(0)

        Tkinter.Radiobutton(self, text="331", variable=self.modl_selection, value=0,
                            font=(Window.FONT, Window.FONT_SIZE),
                            command=self.modlselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="340", variable=self.modl_selection, value=1,
                            font=(Window.FONT, Window.FONT_SIZE),
                            command=self.modlselect).grid(row=r, column=2)

        r += 1

        """HEATER POWER RANGE"""
        Tkinter.Label(self, text="Heater Power:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.range = [0., 0.5, 5.].index(self.lj.read_heater_range())
        self.range_selection = Tkinter.IntVar(self)

        self.range_selection.set(self.range)

        Tkinter.Radiobutton(self, text="0.0 W", variable=self.range_selection, value=0,
                            font=(Window.FONT, Window.FONT_SIZE),
                            command=self.rangeselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="0.5 W", variable=self.range_selection, value=1,
                            font=(Window.FONT, Window.FONT_SIZE),
                            command=self.rangeselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="5.0 W", variable=self.range_selection, value=2,
                            font=(Window.FONT, Window.FONT_SIZE),
                            command=self.rangeselect).grid(row=r, column=3)

        r += 1

        """RAMP"""
        Tkinter.Label(self, text="Ramp [K/min]:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.ramp = self.lj.read_ramp_speed()
        self.ramp_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.ramp_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.ramp_entry.insert(0, self.ramp)

        Tkinter.Button(self, text="SET",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.set_ramp).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """SETPOINT"""
        Tkinter.Label(self, text="Setpoint [K]:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.stpt = self.lj.read_setpoint()
        self.stpt_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.stpt_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.stpt_entry.insert(0, self.stpt)

        Tkinter.Button(self, text="SET",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.set_stpt).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        Tkinter.Button(self, text="UPDATE",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.update_stpt).grid(row=r, column=3, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """PID"""
        Tkinter.Label(self, text="PID [P, I, D]:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.pid = self.lj.read_PID()
        self.pid_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.pid_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.pid_entry.insert(0, str(self.pid).strip('[').strip(']'))

        Tkinter.Button(self, text="SET",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.set_pid).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """READ TEMPERATURE"""
        Tkinter.Label(self, text="Read Temperature [K]:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.temp = self.lj.read_temp()
        self.temp_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.temp_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.temp_entry.insert(0, self.temp)

        Tkinter.Button(self, text="UPDATE",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.update_temp).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """READ HEATER OUTPUT"""
        Tkinter.Label(self, text="Read Heater Output [%]:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.hout = self.lj.read_heater()
        self.hout_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.hout_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.hout_entry.insert(0, self.hout)

        Tkinter.Button(self, text="UPDATE",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.update_hout).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """READ RAMP STATUS"""
        Tkinter.Label(self, text="Ramp Status:",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.r_st = str(self.lj.read_ramp_status())
        self.r_st_entry = Tkinter.Entry(self, font=(Window.FONT, Window.FONT_SIZE))
        self.r_st_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.r_st_entry.insert(0, self.r_st)

        Tkinter.Button(self, text="UPDATE",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.update_r_st).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """QUIT BUTTON"""
        Tkinter.Button(self, text="QUIT",
                       font=(Window.FONT, Window.FONT_SIZE),
                       command=self.quit).grid(row=r, column=columns, sticky=Tkinter.E + Tkinter.W)
        r += 1
        Tkinter.Label(self, text="2021 Teddy Tortorici",
                      font=(Window.FONT, Window.FONT_SIZE)).grid(row=r, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # self.attributes('-topmost', True)

    def rangeselect(self):
        if self.range_selection.get() == 0:
            self.range = 0.
        elif self.range_selection.get() == 1:
            self.range = 0.5
        elif self.range_selection.get() == 2:
            self.range = 5.
        self.lj.set_heater_range(self.range)

    def modlselect(self):
        if self.modl_selection.get() == 0:
            if self.modl != 331:
                self.lj = tools.LakeShore(self.port)
                self.modl = 331
        elif self.modl_selection.get() == 1:
            if self.modl != 340:
                self.lj = tools.LakeShore(self.port, 340)
                self.modl = 340

    def set_pid(self):
        pid = self.pid_entry.get().split(',')
        if len(pid) == 3:
            self.lj.set_PID(pid[0], pid[1], pid[2])
            self.pid = self.pid_entry.get().split(',')
        self.pid_entry.delete(0, 'end')
        self.stpt_entry.insert(0, str(self.pid).strip('[').strip(']'))

    def set_port(self):
        self.port = int(self.port_entry.get())
        self.lj = tools.LakeShore(self.port)

    def set_ramp(self):
        self.ramp = float(self.ramp_entry.get())
        self.lj.set_ramp_speed(self.ramp)

    def set_stpt(self):
        self.stpt = float(self.stpt_entry.get())
        self.lj.set_setpoint(self.stpt)

    def update_r_st(self):
        self.r_st = str(self.lj.read_ramp_status())
        self.r_st_entry.delete(0, 'end')
        self.r_st_entry.insert(0, self.r_st)

    def update_stpt(self):
        self.stpt = self.lj.read_setpoint()
        self.stpt_entry.delete(0, 'end')
        self.stpt_entry.insert(0, self.stpt)

    def update_temp(self):
        self.temp = self.lj.read_temp()
        self.temp_entry.delete(0, 'end')
        self.temp_entry.insert(0, self.temp)

    def update_hout(self):
        self.hout = self.lj.read_heater()
        self.hout_entry.delete(0, 'end')
        self.hout_entry.insert(0, self.hout)

    def quit(self):
        self.destroy()


def start():
    Window().mainloop()


if __name__ == '__main__':
    Window().mainloop()