# This Python file uses the following encoding: utf-8

import PyInstaller.__main__
import os

os.system("pyside6-uic form.ui -o ui_form.py")
PyInstaller.__main__.run(['Open-FM.spec'])
