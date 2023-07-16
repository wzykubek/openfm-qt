# coding=utf-8

import json

import requests
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStyle

from . import API_URL, DEFAULT_VOLUME, Ui_MainWindow

from __feature__ import snake_case  # isort: skip


class MainWindow(QMainWindow):
    """MainWindow Class."""

    def __init__(self, parent=None):
        """Initialize UI, audio player and handlers."""
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        volume_icon = self.style().standard_icon(QStyle.SP_MediaVolume)
        playback_icon = self.style().standard_icon(QStyle.SP_MediaPlay)
        self.ui.volumeToolButton.icon = volume_icon
        self.ui.playbackToolButton.icon = playback_icon

        self.__stations_data = self.getStationsData()
        self.__player = QMediaPlayer()
        self.__audio = QAudioOutput()
        self.__player.audio_output = self.__audio
        self.printGroups()

        self.setVolume(DEFAULT_VOLUME)
        self.ui.volumeHorizontalSlider.value = DEFAULT_VOLUME

        self.ui.groupsListWidget.itemClicked.connect(self.printStations)
        self.ui.stationsListWidget.itemClicked.connect(self.playRadio)
        self.ui.playbackToolButton.clicked.connect(self.togglePlayer)
        self.ui.volumeHorizontalSlider.valueChanged.connect(self.setVolume)
        self.ui.volumeToolButton.clicked.connect(self.toggleMute)

    def getStationsData(self) -> dict:
        """Get JSON data from API and convert it to dict."""
        try:
            resp = requests.get(API_URL)
            if resp.status_code not in range(200, 299 + 1):
                raise requests.exceptions.ConnectionError()
            else:
                return json.loads(resp.text)
        except requests.exceptions.ConnectionError:
            error_box = QMessageBox.critical(
                self,
                "Błąd",
                "Brak połączenia z serwerem.",
                QMessageBox.Cancel,
            )
            error_box.exec()

    def printGroups(self) -> None:
        """Print groups (categories) in groupsListWidget."""
        self.ui.groupsListWidget.add_items(
            [e["name"] for e in self.__stations_data["groups"]])

    def printStations(self) -> None:
        """Print stations (channels) in stationsListWidget."""
        group = self.ui.groupsListWidget.selected_items()[0].text()
        group_id = None
        for e in self.__stations_data["groups"]:
            if e["name"] == group:
                group_id = e["id"]

        self.ui.stationsListWidget.clear()
        self.ui.stationsListWidget.add_items([
            e["name"] for e in self.__stations_data["channels"]
            if e["group_id"] == group_id
        ])

    def setVolume(self, volume: int = None) -> None:
        """Set playback volume to given number or slider value."""
        if not volume:
            volume = self.ui.volumeHorizontalSlider.value
        self.__audio.volume = volume / 100

    def toggleMute(self) -> None:
        """Toggle playback volume between 0 and DEFAULT_VOLUME."""
        if self.ui.volumeHorizontalSlider.value == 0:
            self.ui.volumeHorizontalSlider.value = self.previous_volume
            icon = self.style().standard_icon(QStyle.SP_MediaVolume)
            self.setVolume(self.previous_volume)
        else:
            self.previous_volume = self.__audio.volume * 100
            self.ui.volumeHorizontalSlider.value = 0
            icon = self.style().standard_icon(QStyle.SP_MediaVolumeMuted)
            self.setVolume(0)

        self.ui.volumeToolButton.icon = icon

    def playRadio(self) -> None:
        """Play station selected by user."""
        station = self.ui.stationsListWidget.selected_items()[0].text()
        stream_url = None
        for e in self.__stations_data["channels"]:
            if e["name"] == station:
                stream_url = f"http://stream.open.fm/{e['id']}"

        self.__player.source = QUrl(stream_url)
        self.window_title = f"Open FM - {station}"

        # Required to avoid crashing. For some reason if you want to change
        # the station for the first time, you need to stop and resume playback.
        # If you won't, application would crash.
        for _ in range(3):
            self.togglePlayer()

    def togglePlayer(self) -> None:
        """Toggle playback (play/stop)."""
        pb_state = QMediaPlayer.PlaybackState
        if self.__player.playback_state == pb_state.PlayingState:
            self.__player.stop()
            icon = self.style().standard_icon(QStyle.SP_MediaPlay)
        elif self.__player.playback_state == pb_state.StoppedState:
            self.__player.play()
            icon = self.style().standard_icon(QStyle.SP_MediaStop)
        else:
            pass

        self.ui.playbackToolButton.icon = icon
