

if __name__ == "__main__":
    data = data_files.DielectricSpec(path=path,
                                     filename=filename,
                                     frequencies=dialog.frequencies,
                                     bridge=bridge,
                                     ls_model=ls_num,
                                     comment=full_comment)
    self.data.initiate_devices(voltage_rms=self.dialog.voltage,
                               averaging_setting=self.dialog.averaging,
                               dc_setting=self.dialog.dc_bias_setting)
    self.plot_initializer.signal.emit(os.path.join(path, filename))
    self.parent.control_tab.initialize_controller()
    self.start()