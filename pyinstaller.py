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

import itertools
import os
import shutil
from datetime import datetime
from pathlib import Path

import toml as toml
from PyInstaller.__main__ import run
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, \
    StringStruct, VarFileInfo, VarStruct, SetVersion

from hdlg.config import Directories

"""PyInstaller Configuration"""
DEBUG = False  # When False, removes un-needed data after build has finished
ONE_FILE = False  # Must be False if using Inno Setup
CONSOLE = False  # If build is intended for GUI, set to False
ICON_FILE = None  # pass None to use default icon
ADDITIONAL_DATA = [
    # local file path, destination in build output
    #["hdlg/images", "hdlg/images"],
    ["hdlg/ui/main.ui", "hdlg/ui"],
    ["hdlg/ui/app.qss", "hdlg/ui"],
    ["hdlg/ui/icons", "hdlg/ui/icons"],
]
HIDDEN_IMPORTS = ["PySide2.QtXml"]
EXTRA_ARGS = [
    "-y", "--win-private-assemblies", "--win-no-prefer-redirects"
]

"""Project Configuration"""
project = toml.load(Directories.root.parent / "pyproject.toml")["tool"]["poetry"]
NAME = "HDLG"
AUTHOR = project["authors"][0].split(" <")[0]
VERSION = project["version"]
DESCRIPTION = project["description"]
ENTRY_POINT = "hdlg/hdlg.py"

"""Prepare environment to ensure output data is fresh."""
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
Path(f"{NAME}.spec").unlink(missing_ok=True)

"""Run PyInstaller with the provided configuration."""
run([
    ENTRY_POINT,
    "-n", NAME,
    "-i", ICON_FILE or "NONE",
    ["-D", "-F"][ONE_FILE],
    ["-w", "-c"][CONSOLE],
    *itertools.chain(*[["--add-data", os.pathsep.join(x)] for x in ADDITIONAL_DATA]),
    *itertools.chain(*[["--hidden-import", x] for x in HIDDEN_IMPORTS]),
    *EXTRA_ARGS
])

"""Set Version Info Structure."""
VERSION_4_TUP = tuple(map(int, ("%s.0" % VERSION).split(".")))
VERSION_4_STR = ".".join(map(str, VERSION_4_TUP))
SetVersion(
    ["dist/{0}/{0}", "dist/{0}"][ONE_FILE].format(NAME) + ".exe",
    VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=VERSION_4_TUP,
            prodvers=VERSION_4_TUP
        ),
        kids=[
            StringFileInfo([StringTable(
                "040904B0",  # ?
                [
                    StringStruct("Comments", NAME),
                    StringStruct("CompanyName", AUTHOR),
                    StringStruct("FileDescription", DESCRIPTION),
                    StringStruct("FileVersion", VERSION_4_STR),
                    StringStruct("InternalName", NAME),
                    StringStruct("LegalCopyright", f"Copyright (C) {datetime.now().year} {AUTHOR}"),
                    StringStruct("OriginalFilename", ""),
                    StringStruct("ProductName", NAME),
                    StringStruct("ProductVersion", VERSION_4_STR)
                ]
            )]),
            VarFileInfo([VarStruct("Translation", [0, 1200])])  # ?
        ]
    )
)

if not DEBUG:
    shutil.rmtree("build", ignore_errors=True)
    Path(f"{NAME}.spec").unlink(missing_ok=True)
