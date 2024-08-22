# No longer in Development

I no longer own any PS2 systems, nor plan to in the future. Therefore, I cannot test any updates to this.  
Feel free to fork this project and continue it, including using any of the artwork, just please follow the license.  
If you have a successful fork that eventually trumps this original project repo, please let me know.

* * *

![Banner](https://rawcdn.githack.com/rlaphoenix/hdlg/50bab8126da83a63e83bf6a5ce3d4d1f737ced2b/banner.png)

[![Build status](https://github.com/rlaphoenix/hdlg/actions/workflows/ci.yml/badge.svg)](https://github.com/rlaphoenix/hdlg/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/hdlg)](https://pypi.python.org/pypi/hdlg)
[![Python versions](https://img.shields.io/pypi/pyversions/hdlg)](https://pypi.python.org/pypi/hdlg)
<a href="https://github.com/rlaphoenix/hdlg/blob/master/LICENSE">
  <img align="right" src="https://img.shields.io/badge/license-GPLv3-blue" alt="License (GPLv3)"/>
</a>

HDLG is a modern GUI for hdl-dump with Batch installation capabilities.

**hdl-dump**: <https://github.com/ps2homebrew/hdl-dump>  
**wLaunchELF**: <https://github.com/ps2homebrew/wLaunchELF>

![Preview](https://user-images.githubusercontent.com/17136956/198822365-f244dcf6-3050-45f2-83dd-c32c4d36f976.png)  
*Preview as of October 2022.*

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
- [x] Show HDD information like Disk Size, Space Used, and such.
- [x] Add ability to install a new game to selected HDD.
- [x] Add batch installation support by selecting more than one file.
- [ ] Create a file based settings system.
- [ ] Add per-install settings like startup, flags, and DMA mode.
- [ ] Add ability to format an HDD for use with a PS2 with `pfsshell`.
- [ ] Add ability to rename the Game Name of installed games.
- [ ] Add ability to extract an installed game from the PS2 HDD.
- [ ] Add ability to view an installed game's sector table.
- [ ] Add ability to set a custom icon to an installed game.
- [ ] Add remote PS2 HDD (samba) connection option.
- [ ] Add Inno Setup script.
- [ ] Add Linux support.
- [ ] Add macOS support.

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
