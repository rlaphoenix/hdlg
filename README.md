# HDLG

[![GPLv3 license](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/rlaphoenix/hdlg/blob/master/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/hdlg)](https://pypi.org/project/hdlg)
[![Python versions](https://img.shields.io/pypi/pyversions/hdlg)](https://pypi.org/project/hdlg)
[![PyPI status](https://img.shields.io/pypi/status/hdlg)](https://pypi.org/project/hdlg)
[![Contributors](https://img.shields.io/github/contributors/rlaphoenix/hdlg)](https://github.com/rlaphoenix/hdlg/graphs/contributors)
[![GitHub issues](https://img.shields.io/github/issues/rlaphoenix/hdlg)](https://github.com/rlaphoenix/hdlg/issues)
![Build](https://github.com/rlaphoenix/hdlg/workflows/Build/badge.svg?branch=master)

HDLG is a modern cross-platform GUI for hdl-dump with Batch installation capabilities.

## Looking for Artwork

This project is looking for an Icon and Text Logo as well as a Banner artwork. If you have some free time and would
like to contribute artwork to the project, let me know!

## Installation

    pip install --user hdlg

To run hdlg, type `hdlg` into any terminal, command prompt, app launcher, or the start menu.

If you wish to manually install from the source, take a look at [Building](#building-source-and-wheel-distributions).

## To-do

- [x] Craft initial GUI with Qt.
- [x] Push to PyPI and add relevant Badges.
- [x] Add PyInstaller make file.
- [x] Add local PS2 HDD connection option.
- [x] List installed games of selected HDD.
- [ ] Show HDD information like Disk Size, Space Used, and such.
- [ ] Add ability to install a new game to selected HDD.
- [ ] Create a file based settings system.
- [ ] Add remote PS2 HDD (samba) connection option.

## Building

This project requires [Poetry], so feel free to take advantage and use it for its various conveniences like
building sdist/wheel packages, creating and managing dependencies, virtual environments, and more.

Note:

- Source Code may have changes that may be old, not yet tested or stable, or may have regressions.
- Only run or install from Source Code if you have a good reason. Examples would be to test for regressions, test
  changes (either your own or other contributors), or to research the code (agreeing to the [LICENSE](LICENSE)).
- [Poetry] is required as it's used as the [PEP 517] build system, virtual environment manager, dependency manager,
  and more.

  [Poetry]: <https://python-poetry.org/docs/#installation>
  [PEP 517]: <https://www.python.org/dev/peps/pep-0517>

### Install from Source Code

    git clone https://github.com/rlaphoenix/hdlg.git
    cd hdlg
    pip install --user .

### Building source and wheel distributions

    poetry build

You can specify `-f` to build `sdist` or `wheel` only. Built files can be found in the `/dist` directory.

### Packing with PyInstaller

    poetry run python pyinstaller.py

The build is now available at `./dist`.
