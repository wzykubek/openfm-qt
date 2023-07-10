# coding=utf-8

import sys
import os
from shutil import which

UI_DIR = "assets/ui"


class UICNotFound(Exception):
    pass


if sys.platform == "linux":
    exe = "pyside6-uic"
    exe_alt = "/usr/lib/qt6/uic"
elif sys.platform == "win32":
    exe = "pyside6-uic.exe"
    exe_alt = None

if not which(exe) and not which(exe_alt):
    raise UICNotFound("User Interface Compiler binary not found.")
elif not which(exe) and which(exe_alt):
    exe = exe_alt

for f in os.listdir(UI_DIR):
    if exe == "/usr/lib/qt6/uic":
        __flags = "--generator python"
    os.system(f"{exe} {UI_DIR}/{f} -o openfm_qt/ui_{f[:-3]}.py {__flags}")
