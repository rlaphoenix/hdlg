"""
hdlg - Modern cross-platform GUI for hdl-dump.
Copyright (C) 2021 rlaphoenix

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

from pathlib import Path

from appdirs import AppDirs


class Directories:
    app_dirs = AppDirs("hdlg", False)
    root = Path(__file__).resolve().parent  # root of package/src


class Files:
    @staticmethod
    def qss(name):
        return (Directories.root / "ui" / f"{name}.qss").read_text("utf8")

