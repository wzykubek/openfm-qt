# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow
import json
import requests


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.stations_slug = json.loads(requests.get(
            "https://open.fm/radio/api/v2/ofm/stations_slug.json"
        ).text)
        self.getGroups()
        self.ui.groupslistWidget.itemClicked.connect(self.getStations)

    def getGroups(self):
        for el in self.stations_slug["groups"]:
            self.ui.groupslistWidget.addItem(el["name"])

    def getStations(self):
        group = self.ui.groupslistWidget.selectedItems()[0].text()
        group_id = None
        for i in self.stations_slug["groups"]:
            if i["name"] == group:
                group_id = i["id"]

        self.ui.stationslistWidget.clear()
        for ch in self.stations_slug["channels"]:
            if ch["group_id"] == group_id:
                self.ui.stationslistWidget.addItem(ch["name"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
