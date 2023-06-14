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

API_URL = "https://open.fm/radio/api/v2/ofm/stations_slug.json"
DEFAULT_VOLUME = 70


class MainWindow(QMainWindow):
    """MainWindow Class."""

    def __init__(self, parent=None):
        """Initialize UI, audio player and handlers."""
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__stations_data = self.getStationsData()
        self.__player = QMediaPlayer()
        self.__audio = QAudioOutput()
        self.__player.setAudioOutput(self.__audio)
        self.setVolume(DEFAULT_VOLUME)
        self.printGroups()
        self.ui.groupsListWidget.itemClicked.connect(self.printStations)
        self.ui.stationsListWidget.itemClicked.connect(self.playRadio)
        self.ui.playbackToolButton.clicked.connect(self.togglePlayer)
        self.ui.volumeHorizontalSlider.valueChanged.connect(self.setVolume)
        self.ui.volumeToolButton.clicked.connect(self.toggleMute)

    def getStationsData(self) -> dict:
        """Get JSON data from API and convert it to dict."""
        resp = requests.get(API_URL)
        if resp.status_code not in range(200, 299 + 1):
            error_box = QMessageBox.critical(
                self,
                "Błąd",
                f"Błąd połączenia o kodzie: {resp.status_code}",
                QMessageBox.Cancel,
            )
            error_box.exec()
        else:
            return json.loads(resp.text)

    def printGroups(self) -> None:
        """Print groups (categories) in groupsListWidget."""
        self.ui.groupsListWidget.addItems(
            [e["name"] for e in self.__stations_data["groups"]]
        )

    def printStations(self) -> None:
        """Print stations (channels) in stationsListWidget."""
        group = self.ui.groupsListWidget.selectedItems()[0].text()
        group_id = None
        for e in self.__stations_data["groups"]:
            if e["name"] == group:
                group_id = e["id"]

        self.ui.stationsListWidget.clear()
        self.ui.stationsListWidget.addItems(
            [
                e["name"]
                for e in self.__stations_data["channels"]
                if e["group_id"] == group_id
            ]
        )

    def setVolume(self, volume: int = None) -> None:
        """Set playback volume to given number or slider value."""
        if not volume:
            volume = self.ui.volumeHorizontalSlider.value()
        self.__audio.setVolume(volume / 100)

    def toggleMute(self) -> None:
        """Toggle playback volume between 0 and DEFAULT_VOLUME."""
        if self.ui.volumeHorizontalSlider.value() == 0:
            self.ui.volumeHorizontalSlider.setValue(DEFAULT_VOLUME)
            self.ui.volumeToolButton.setIcon(
                QIcon.fromTheme("audio-volume-medium")
            )
            self.setVolume(DEFAULT_VOLUME)
        else:
            self.ui.volumeHorizontalSlider.setValue(0)
            self.ui.volumeToolButton.setIcon(
                QIcon.fromTheme("audio-volume-muted")
            )
            self.setVolume(0)

    def playRadio(self) -> None:
        """Play station selected by user."""
        station = self.ui.stationsListWidget.selectedItems()[0].text()
        stream_url = None
        for e in self.__stations_data["channels"]:
            if e["name"] == station:
                stream_url = f"http://stream.open.fm/{e['id']}"

        self.__player.setSource(QUrl(stream_url))
        self.ui.playbackToolButton.setIcon(
            QIcon.fromTheme("media-playback-start")
        )
        self.togglePlayer()

    def togglePlayer(self) -> None:
        """Toggle playback (play/stop)."""
        pb_state = QMediaPlayer.PlaybackState
        if self.__player.playbackState() == pb_state.PlayingState:
            self.__player.stop()
            self.ui.playbackToolButton.setIcon(
                QIcon.fromTheme("media-playback-start")
            )
        elif self.__player.playbackState() == pb_state.StoppedState:
            self.__player.play()
            self.ui.playbackToolButton.setIcon(
                QIcon.fromTheme("media-playback-stop")
            )
        else:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
