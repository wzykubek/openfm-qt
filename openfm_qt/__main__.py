# coding=utf-8

import sys

from PySide6.QtWidgets import QApplication

from . import MainWindow


def main():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
