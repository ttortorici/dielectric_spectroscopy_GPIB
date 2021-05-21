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


class Setup_Window(Tkinter.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    LJ_CHs = 4

    def __init__(self):
        print('\n\n\n')
        """establish the day data is getting taken
        self.date has attributes .year, .month, .day, .hour, .min, .second, .microsecond"""
        self.date = datetime.datetime.fromtimestamp(time.time())

        # get filepath in googledrive
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
        self.title('Measure Capacitance')

        """
        create and place labels
        """
        columns = 3

        r = 0

        """TITLE LINE"""
        Tkinter.Label(self, text='Control LakeShore Temperature Controller',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)

        r += 1

        """PORT FOR SERVER COMM"""
        Tkinter.Label(self, text="Port to communicate with GPIB server:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.port = 62535
        self.port_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.port_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.port_entry.insert(0, self.port)

        Tkinter.Button(self, text="SET",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.set_port).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)
        self.lj = None
        self.set_port()

        r += 1

        """HEATER POWER RANGE"""
        Tkinter.Label(self, text="Heater Power:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.range = [0., 0.5, 5.].index(self.lj.read_range())
        self.range_selection = Tkinter.IntVar(self)

        self.range_selection.set(0)

        Tkinter.Radiobutton(self, text="0.0 W", variable=self.inst_selection, value=0,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.rangeselect).grid(row=r, column=1)
        Tkinter.Radiobutton(self, text="0.5 W", variable=self.inst_selection, value=1,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.rangeselect).grid(row=r, column=2)
        Tkinter.Radiobutton(self, text="5.0 W", variable=self.inst_selection, value=2,
                            font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                            command=self.rangeselect).grid(row=r, column=3)

        r += 1

        """RAMP"""
        Tkinter.Label(self, text="Ramp [K/min]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.ramp = self.lj.read_ramp_speed()
        self.ramp_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.ramp_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.ramp_entry.insert(0, self.ramp)

        Tkinter.Button(self, text="SET",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.set_ramp).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """SETPOINT"""
        Tkinter.Label(self, text="Setpoint [K]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.stpt = self.lj.read_setpoint()
        self.stpt_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.stpt_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.stpt_entry.insert(0, self.stpt)

        Tkinter.Button(self, text="SET",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.set_stpt).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """READ TEMPERATURE"""
        Tkinter.Label(self, text="Read Temperature [K]:",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=Tkinter.W)
        self.temp = self.lj.read_temp()
        self.temp_entry = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.temp_entry.grid(row=r, column=1, sticky=Tkinter.E + Tkinter.W)
        self.temp_entry.insert(0, self.temp)

        Tkinter.Button(self, text="UPDATE",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.update_temp).grid(row=r, column=2, sticky=Tkinter.E + Tkinter.W)

        r += 1

        """QUIT BUTTON"""
        Tkinter.Button(self, text="QUIT",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.quit).grid(row=r, column=columns, sticky=Tkinter.E + Tkinter.W)
        r += 1
        Tkinter.Label(self, text="2021 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.killWindow)

        # self.attributes('-topmost', True)

    def rangeselect(self):
        if self.range_selection.get() == 0:
            self.range = 0.
        elif self.range_selection.get() == 1:
            self.range = 0.5
        elif self.range_selection.get() == 2:
            self.range = 5.
        self.lj.set_heater_range(self.range)

    def set_port(self):
        self.port = int(self.port_entry.get())
        self.lj = tools.LakeShore(self.port)

    def set_ramp(self):
        self.ramp = float(self.ramp_entry.get())
        self.lj.set_ramp_speed(self.ramp)

    def set_stpt(self):
        self.stpt = float(self.stpt_entry.get())
        self.lj.set_setpoint(self.stpt)

    def update_temp(self):
        self.temp = self.lj.read_temp()
        self.temp_entry.delete(0, 'end')
        self.temp_entry.insert(0, self.temp)

    def quit(self):
        self.destroy()
