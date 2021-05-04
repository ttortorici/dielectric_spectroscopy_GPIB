class Setup_Window(Tkinter.Tk):

    FONT_SIZE = 10
    FONT = 'Arial'

    time_axis = 'hr'
    titles = ['Capacitance vs Time',
              'Capacitance vs Temperature',
              'Loss vs Time',
              'Loss vs Temperature',
              'Capacitance and Loss vs Time',
              'Capacitance and Loss vs Temperature',
              'Log2 omega vs inverse T of Loss Peak']
    axes_labelss = [['Time [%s]' % time_axis, 'Capacitance [pF]', 'Temperature [K]'],
                    ['Temperature [K]', 'Capacitance [pF]'],
                    ['Time [%s]' % time_axis, 'Loss Tangent', 'Temperature [K]'],
                    ['Temperature [K]', 'Loss Tangent'],
                    ['Time [%s]' % time_axis, 'Loss Tangent', 'Capacitance [pF]'],
                    ['Temperature [K]', 'Loss Tangent', 'Capacitance [pF]'],
                    ['1/T [1/K]', 'Log2(omega)']]
    legend_locs = ['best', 'best', 'best', 'best', 'best', 'best', 'best']
    plot_ranges = [[False, False], [False], [False, False], [False], [False, False], [False, False], [False, False]]
    start_trim = 0
    end_trim = None
    time_trims = [[start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim],
                 [start_trim, end_trim]]

    def __init__(self):
        """Initialize"""
        """determine time factor"""
        if 'min' in Setup_Window.time_axis.lower():
            self.time_factor = 60
        elif 'hr' in Setup_Window.time_axis.lower():
            self.time_factor = 60 * 60
        else:
            raise ValueError('Setup_Window.time_axis has an invalid value')

        """establish the day data is getting taken"""
        date = str(datetime.date.today()).split('-')
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]

        """replace date with sys.argv entry"""
        if len(sys.argv) >= 2:
            datemsg = sys.argv[1].split('-')
            if len(datemsg) == 2:
                self.month = datemsg[0]
                self.day = datemsg[1]
            elif len(datemsg) == 3:
                self.year = datemsg[2]
                self.month = datemsg[0]
                self.day = datemsg[1]
            elif len(datemsg) == 1:
                try:
                    day_temp = int(datemsg[0])
                    if day_temp > int(self.day):
                        self.month = str(int(self.month) - 1)
                        if int(self.month) == 0:
                            self.month = '12'
                    self.day = datemsg[0]
                except ValueError:
                    pass

        """make sure the numbers come out right"""
        if len(self.day) == 1:
            self.day = '0' + self.day
        if len(self.month) == 1:
            self.month = '0' + self.month
        if len(self.year) == 2:
            self.year = '20' + self.year

        """get filepath in googledrive"""
        self.path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', self.year, self.month, self.day)

        """get list of files in this directory"""
        filenames = data_files.file_name(self.month, self.day, self.year)
        self.filenames = []
        for f in filenames[0]:
            if not '_sorted' in f.lower() and 'cooling' in f.lower():
                self.filenames.append(f)
        print 'All the files in the directory: ' + str(self.filenames)

        # set up window
        Tkinter.Tk.__init__(self)
        self.title('Plot Present 4')

        Tkinter.Label(self, text='Select the files you would like to plot:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=0, column=0, sticky=Tkinter.W)

        """place checkbox list"""
        self.var_list = [0] * len(self.filenames)
        check_list = [0] * len(self.filenames)
        for ii, f in enumerate(self.filenames):
            comment = self.get_comment(f)       # grab comment from the file
            flength = self.count_rows(f)        # determine number of rows in file
            Tkinter.Label(self, text=comment,
                          font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=ii+1, column=0, sticky=Tkinter.W)
            self.var_list[ii] = Tkinter.IntVar()
            Tkinter.Checkbutton(self, text='%d rows in file' % flength,
                                variable=self.var_list[ii]).grid(row=ii+1, column=1, sticky=Tkinter.E + Tkinter.W)
            self.var_list[ii].set(1)

        next_row = len(self.filenames) + 1

        """Set Capacitance plotting range"""
        Tkinter.Label(self, text='Capacitance Range [pF]:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=next_row, column=1,
                                                                             sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_low = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_range_entry_low.grid(row=next_row, column=2, sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_low.insert(0, cap_str_low)
        self.cap_range_entry_high = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.cap_range_entry_high.grid(row=next_row, column=3, sticky=Tkinter.E + Tkinter.W)
        self.cap_range_entry_high.insert(0, cap_str_high)

        next_row += 1

        """Set Loss plotting range"""
        Tkinter.Label(self, text='Loss Tangent range:',
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=next_row, column=1,
                                                                             sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_low = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.loss_range_entry_low.grid(row=next_row, column=2, sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_low.insert(0, loss_str_low)
        self.loss_range_entry_high = Tkinter.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.loss_range_entry_high.grid(row=next_row, column=3, sticky=Tkinter.E + Tkinter.W)
        self.loss_range_entry_high.insert(0, loss_str_high)

        next_row += 1

        """Create and place buttons"""
        Tkinter.Button(self, text="Go",
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                       command=self.go).grid(row=next_row, column=1, sticky=Tkinter.E + Tkinter.W)
        next_row += 1
        Tkinter.Label(self, text="2017 Teddy Tortorici",
                      font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=next_row, column=0, columnspan=2,
                                                                             sticky=Tkinter.W, padx=1, pady=1)

        # Organize cleanup
        self.protocol("WM_DELETE_WINDOW", self.cleanUp)

        self.attributes('-topmost', True)

    def go(self):
        self.files_to_use = []
        for ii, var in enumerate(self.var_list):
            file_bool = var.get()
            if file_bool:
                self.files_to_use.append(self.filenames[ii])
        print "These files were selected: " + str(self.files_to_use)
        self.cap_range = [float(self.cap_range_entry_low.get()), float(self.cap_range_entry_high.get())]
        self.loss_range = [float(self.loss_range_entry_low.get()), float(self.loss_range_entry_high.get())]

        self.load_data()

        self.cleanUp()

        for title, axes_labels, time_trim, legend_loc, plot_range in zip(Setup_Window.titles,
                                                                         Setup_Window.axes_labelss,
                                                                         Setup_Window.time_trims,
                                                                         Setup_Window.legend_locs,
                                                                         Setup_Window.plot_ranges):
            p = Plot(title, axes_labels, time_trim, legend_loc, plot_range)
            if title == 'Capacitance vs Time':
                p.plot_sep_freq(self.timestamps, self.capacitance, self.freqs, self.cap_range)
                p.plot(self.timestamps, self.temperature1, plot_range[1],
                       marker='r--', label='Stage A Temperature', ax='R')
                p.plot(self.timestamps, self.temperature2, plot_range[1],
                       marker='b--', label='Stage B Temperature', ax='R')
            elif title == 'Capacitance vs Temperature':
                p.plot_sep_freq(self.temperature1, self.capacitance,
                                self.freqs, self.cap_range)
            elif title == 'Loss vs Time':
                p.plot_sep_freq(self.timestamps, self.loss, self.freqs, self.loss_range)
                p.plot(self.timestamps, self.temperature1, plot_range[1],
                       marker='r--', label='Stage A Temperature', ax='R')
                p.plot(self.timestamps, self.temperature2, plot_range[1],
                       marker='b--', label='Stage B Temperature', ax='R')
            elif title == 'Loss vs Temperature':
                p.plot_sep_freq(self.temperature1, self.loss, self.freqs, self.loss_range)
            elif title == 'Capacitance and Loss vs Time':
                p.plot_sep_freq(self.timestamps, self.capacitance, self.freqs, self.cap_range,
                                label='Capacitance', ax='R')
                p.plot_sep_freq(self.timestamps, self.loss, self.freqs, self.loss_range, label='Loss')
            elif title == 'Capacitance and Loss vs Temperature':
                p.plot_sep_freq(self.temperature1, self.capacitance, self.freqs, self.cap_range,
                                label='Capicatance', ax='R')
                p.plot_sep_freq(self.temperature1, self.loss, self.freqs, self.loss_range, label='Loss')

            m = self.month + '_'
            path_to_save = os.path.join(get.googledrive(), 'Dielectric_data', 'Graphs', self.year,
                                        m + calendar.month_name[int(self.month)],
                                        self.day)

            plt.legend(loc=legend_loc)

            if not os.path.exists(path_to_save):
                os.makedirs(path_to_save)

            plt.savefig(os.path.join(path_to_save, title),
                        dpi=None, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches=None, pad_inches=0.1,
                        frameon=None)
        plt.show()


    def cleanUp(self):
        """Close window"""
        self.destroy()