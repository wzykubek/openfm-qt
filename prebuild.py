# coding=utf-8

import sys
import os
from shutil import which
import logging

UI_DIR = "assets/ui"

logging.basicConfig(level=logging.INFO)


class UICNotFound(Exception):
    pass


if sys.platform == "linux":
    exe = "pyside6-uic"
    exe_alt = "/usr/lib/qt6/uic"
elif sys.platform == "win32":
    exe = "pyside6-uic.exe"
    exe_alt = None
    UI_DIR = UI_DIR.replace("/", "\\")

if not which(exe) and not which(exe_alt):
    raise UICNotFound("User Interface Compiler binary not found.")
elif not which(exe) and which(exe_alt):
    exe = exe_alt

logging.info("Building UI files...")
for f in os.listdir(UI_DIR):
    if exe == "/usr/lib/qt6/uic":
        __flags = "--generator python"
    else:
        __flags = ""
    cmd = f"{exe} {UI_DIR}/{f} -o openfm_qt/ui_{f[:-3]}.py {__flags}"
    if sys.platform == "win32":
        cmd = cmd.replace("/", "\\")
    os.system(cmd)
    logging.info(f"Successfully builded {f} as ui_{f[:-3]}.py")
