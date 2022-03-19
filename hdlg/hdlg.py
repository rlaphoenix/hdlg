"""
hdlg - Modern GUI for hdl-dump.
Copyright (C) 2021-2022 rlaphoenix

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication

from hdlg.config import Directories
from hdlg.ui.main import Main
from hdlg.utils import require_admin


def main():
    require_admin()

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setStyleSheet((Directories.root / "ui" / "app.qss").read_text("utf8"))

    window = Main()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
