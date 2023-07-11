# coding=utf-8

API_URL = "https://open.fm/radio/api/v2/ofm/stations_slug.json"
DEFAULT_VOLUME = 70

from .ui_main_window import Ui_MainWindow  # nopep8: E402  isort: skip
from .mainwindow import MainWindow  # nopep8: E402  isort: skip

__all__ = [Ui_MainWindow, MainWindow]
