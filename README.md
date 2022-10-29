![Banner](https://rawcdn.githack.com/rlaphoenix/hdlg/50bab8126da83a63e83bf6a5ce3d4d1f737ced2b/banner.png)

[![Build Tests](https://img.shields.io/github/workflow/status/rlaphoenix/hdlg/Build?label=Python%203.6%2B%20builds)](https://github.com/rlaphoenix/hdlg/actions?query=workflow%3A%22build%22)
[![GPLv3 license](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/rlaphoenix/hdlg/blob/master/LICENSE)
<a><img align="right" src="https://img.shields.io/pypi/status/hdlg" alt="Project Status"/></a>

HDLG is a modern GUI for hdl-dump with Batch installation capabilities.

**hdl-dump**: <https://github.com/ps2homebrew/hdl-dump>  
**wLaunchELF**: <https://github.com/ps2homebrew/wLaunchELF>

![Preview](https://user-images.githubusercontent.com/17136956/198775765-6d15b91c-6526-4ad1-af10-d9e7e79c5ca9.png)  
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
- [ ] Show HDD information like Disk Size, Space Used, and such.
- [ ] Add Inno Setup script.
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
