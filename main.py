# This Python file uses the following encoding: utf-8

from PySide6.QtWidgets import QApplication
from openfm_qt import MainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
