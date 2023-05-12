import sys
from PySide6.QtWidgets import QApplication
from gui.plot_window import PlotWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = PlotWindow(sys.argv)
    main_window.show()

    sys.exit(app.exec())
