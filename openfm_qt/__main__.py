# This Python file uses the following encoding: utf-8

from PySide6.QtWidgets import QApplication
from . import MainWindow
import sys

def main():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
