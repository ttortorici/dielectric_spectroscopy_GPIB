import sys
from PySide6.QtWidgets import QApplication
from gui.plot_window import PlotWindow
from gui.signalers import Signaler, MessageSignaler
from files.data import DielectricSpec


class DataHandler:
    def __init__(self, sys_argv):
        self.data_thread = None
        self.running = False
        self.started = False

        self.plot_updater = Signaler()
        self.plot_initializer = MessageSignaler()

        self.base_path = sys.argv[1]
        self.filename = sys.argv[2]
        frequencies = [int(f) for f in sys.argv[3].split(",")]
        voltage = float(sys.argv[4])
        averaging = int(sys.argv[5])
        dc_bias_setting = sys.argv[6]
        bridge = sys.argv[7]
        ls_num = int(sys.argv[8])
        comment = sys.argv[9]
        self.file = DielectricSpec(path=self.base_path,
                                   filename=self.filename,
                                   frequencies=frequencies,
                                   bridge=bridge,
                                   ls_model=ls_num,
                                   comment=comment)
        self.file.initiate_devices(voltage_rms=voltage,
                                   averaging_setting=averaging,
                                   dc_setting=dc_bias_setting)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    data = DataHandler(sys.argv)

    main_window = PlotWidget()
    main_window.show()
    main_window.setStyleSheet("background-color: rgb(43, 43, 32);"
                              "color: rgb(255, 255, 255)")

    sys.exit(app.exec())
