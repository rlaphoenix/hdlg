import logging
import platform
import struct
import sys
from datetime import datetime

from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMessageBox

from hdlg.config import Directories
from hdlg.utils import camel_to_snake, is_frozen


class BaseWindow:
    def __init__(self, name: str, flag=QtCore.Qt.Window) -> None:
        name = camel_to_snake(name)

        loader = QUiLoader()
        loader.setWorkingDirectory(QtCore.QDir(str(Directories.root)))
        ui_file = QtCore.QFile(str(Directories.root / "ui" / f"{name}.ui"))
        ui_file.open(QtCore.QFile.ReadOnly)

        self.window = loader.load(ui_file)
        self.window.setWindowFlags(flag)
        ui_file.close()

        self.log = logging.getLogger(name)

    def show(self) -> None:
        self.window.show()

    def about(self) -> None:
        # TODO: Get information from pyproject.toml
        QMessageBox.about(
            self.window,
            "About HDLG",
            ("HDLG v0.2.1 [%s]" % (
                ",".join(map(str, filter(None, [
                    sys.platform,
                    "%dbit" % (8 * struct.calcsize("P")),
                    platform.python_version(),
                    "frozen" if is_frozen() else None
                ])))
            )) +
            f"<p>Copyright (C) {datetime.now().year} PHOENiX</p>" +
            ("<p>{0}<br/><a href='{1}' style='color:white'>{1}</a></p>".format(
                "Modern GUI for hdl-dump.",
                "https://github.com/rlaphoenix/hdlg"
            ))
        )
