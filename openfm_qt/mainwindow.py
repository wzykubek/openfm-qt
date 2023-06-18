# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStyle
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow
import json
import requests
from . import DEFAULT_VOLUME


class MainWindow(QMainWindow):
    """MainWindow Class."""

    def __init__(self, parent=None):
        """Initialize UI, audio player and handlers."""
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        volume_icon = self.style().standardIcon(QStyle.SP_MediaVolume)
        playback_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.ui.volumeToolButton.setIcon(volume_icon)
        self.ui.playbackToolButton.setIcon(playback_icon)

        self.__stations = self.getData(
            "https://open.fm/radio/api/v2/ofm/stations_slug.json"
        )
        self.__podcasts_groups = self.getData(
            "https://open.fm/api/podcasts/categories"
        )
        self.__player = QMediaPlayer()
        self.__audio = QAudioOutput()
        self.__player.setAudioOutput(self.__audio)
        self.setVolume(DEFAULT_VOLUME)
        self.printRadioGroups()
        self.printPodcastGroups()

        self.ui.radioGroupsListWidget.itemClicked.connect(self.printRadioStations)
        self.ui.podcastGroupsListWidget.itemClicked.connect(self.printPodcasts)
        self.ui.podcastListWidget.itemClicked.connect(self.printPodcastEpisodes)
        self.ui.stationsListWidget.itemClicked.connect(self.playRadio)
        self.ui.playbackToolButton.clicked.connect(self.togglePlayer)
        self.ui.volumeHorizontalSlider.valueChanged.connect(self.setVolume)
        self.ui.volumeToolButton.clicked.connect(self.toggleMute)

    def getData(self, url) -> dict:
        """Get JSON data from API and convert it to dict."""
        resp = requests.get(url)
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

    def printRadioGroups(self) -> None:
        """Print groups (categories) in radioGroupsListWidget."""
        self.ui.stationsListWidget.clear()
        self.ui.radioGroupsListWidget.addItems(
            [e["name"] for e in self.__stations["groups"]]
        )

    def printPodcastGroups(self) -> None:
        """Print groups (categories) in podcastGroupsListWidget."""
        self.ui.stationsListWidget.clear()
        self.ui.podcastGroupsListWidget.addItems(
            [e["name"] for e in self.__podcasts_groups]
        )

    def printRadioStations(self) -> None:
        """Print stations (channels) in stationsListWidget."""
        group = self.ui.radioGroupsListWidget.selectedItems()[0].text()
        group_id = None
        for e in self.__stations["groups"]:
            if e["name"] == group:
                group_id = e["id"]

        self.ui.stationsListWidget.clear()
        self.ui.stationsListWidget.addItems(
            [
                e["name"]
                for e in self.__stations["channels"]
                if e["group_id"] == group_id
            ]
        )

    def printPodcasts(self) -> None:
        """Print podcasts in podcastListWidget."""
        self.ui.stationsListWidget.clear()
        group = self.ui.podcastGroupsListWidget.selectedItems()[0].text()
        group_name = None
        for e in self.__podcasts_groups:
            if e["name"] == group:
                group_name = e["slug"]

        self.__podcasts = self.getData(
            f"https://open.fm/api/podcasts/category/{group_name}"
        )["podcasts"]["content"]
        self.ui.podcastListWidget.clear()
        self.ui.podcastListWidget.addItems(
            [e["title"] for e in self.__podcasts]
        )

    def printPodcastEpisodes(self) -> None:
        """Print podcast episodes in stationsListWidget."""
        podcast_name = self.ui.podcastListWidget.selectedItems()[0].text()
        podcast_id = None
        for e in self.__podcasts:
            if e["title"] == podcast_name:
                podcast_id = e["id"]

        self.__podcast_episodes = self.getData(
            f"https://open.fm/api/podcast/{podcast_id}/episodes"
        )
        self.ui.stationsListWidget.clear()
        self.ui.stationsListWidget.addItems(
            [e["title"] for e in self.__podcast_episodes["content"]]
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
            icon = self.style().standardIcon(QStyle.SP_MediaVolume)
            self.setVolume(DEFAULT_VOLUME)
        else:
            self.ui.volumeHorizontalSlider.setValue(0)
            icon = self.style().standardIcon(QStyle.SP_MediaVolumeMuted)
            self.setVolume(0)

        self.ui.volumeToolButton.setIcon(icon)

    def playRadio(self) -> None:
        """Play station selected by user."""
        selection = self.ui.stationsListWidget.selectedItems()[0].text()
        stream_url = None
        for e in self.__stations["channels"]:
            if e["name"] == selection:
                stream_url = f"http://stream.open.fm/{e['id']}"

        if not stream_url:
            for e in self.__podcast_episodes["content"]:
                if e["title"] == selection:
                    stream_url = e["file"].replace("https", "http")

        self.__player.setSource(QUrl(stream_url))

        # Required to avoid crashing. For some reason if you want to change
        # the station for the first time, you need to stop and resume playback.
        # If you won't, application would crash.
        for _ in range(3):
            self.togglePlayer()

    def togglePlayer(self) -> None:
        """Toggle playback (play/stop)."""
        pb_state = QMediaPlayer.PlaybackState
        if self.__player.playbackState() == pb_state.PlayingState:
            self.__player.stop()
            icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        elif self.__player.playbackState() == pb_state.StoppedState:
            self.__player.play()
            icon = self.style().standardIcon(QStyle.SP_MediaStop)
        else:
            pass

        self.ui.playbackToolButton.setIcon(icon)
