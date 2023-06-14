# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QIcon

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
        self.stations_slug = self.getData()
        self.__player = QMediaPlayer()
        self.__audio = QAudioOutput()
        self.__player.setAudioOutput(self.__audio)
        self.setVolume()
        self.getGroups()
        self.ui.groupslistWidget.itemClicked.connect(self.getStations)
        self.ui.stationslistWidget.itemClicked.connect(self.playRadio)
        self.ui.toolButton.clicked.connect(self.togglePlayer)
        self.ui.volumeHorizontalSlider.valueChanged.connect(self.setVolume)
        self.ui.volumeToolButton.clicked.connect(self.toggleMute)

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

    def getData(self) -> dict:
        resp = requests.get("https://open.fm/radio/api/v2/ofm/stations_slug.json")
        if resp.status_code not in range(200, 299 + 1):
            error_box = QMessageBox.critical(
                self, "Błąd",
                f"Błąd połączenia o kodzie: {resp.status_code}",
                QMessageBox.Cancel
            )
            error_box.exec()
        else:
            return json.loads(resp.text)

    def setVolume(self, volume: int = None):
        if volume is None:
            volume = self.ui.volumeHorizontalSlider.value()
        self.__audio.setVolume(volume / 100)

    def toggleMute(self):
        if self.ui.volumeHorizontalSlider.value() == 0:
            self.ui.volumeHorizontalSlider.setValue(70)
            self.ui.volumeToolButton.setIcon(QIcon.fromTheme("audio-volume-medium"))
            self.setVolume(70)
        else:
            self.ui.volumeHorizontalSlider.setValue(0)
            self.ui.volumeToolButton.setIcon(QIcon.fromTheme("audio-volume-muted"))
            self.setVolume(0)

    def playRadio(self):
        station = self.ui.stationslistWidget.selectedItems()[0].text()
        stream_url = None
        for ch in self.stations_slug["channels"]:
            if ch["name"] == station:
                stream_url = f"http://stream.open.fm/{ch['id']}"

        self.__player.setSource(QUrl(stream_url))
        self.ui.toolButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.togglePlayer()

    def togglePlayer(self):
        if self.__player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.__player.stop()
            self.ui.toolButton.setIcon(QIcon.fromTheme("media-playback-start"))
        elif self.__player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self.__player.play()
            self.ui.toolButton.setIcon(QIcon.fromTheme("media-playback-stop"))
        else:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
