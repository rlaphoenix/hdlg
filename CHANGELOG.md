# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2021-10-16

### Added

- Added two Windows-only dependencies, `WMI` and `pywin32`. These are required for scanning HDDs.
- Created initial Worker class.
- Created HDD class for working with the scanned HDDs.
- Created a Size Unit helper utility for listing file sizes in a more human-readable format.
- Added ability to scan and list HDDs with find_hdds() method in the Worker and add_hdd_button() in the UI class.
- Added ability to clear the list of scanned HDDs with clear_hdd_list() method in the UI class.
- Added ability to clear and re-scan the list of HDDs by clicking the refresh icon.
- Added ability to load a scanned HDD to list HDD information and more with get_hdd_info() method in the Worker and
  use_hdd_info() in the UI class.
- Added ability to list games within an HDD with get_game_list() method in the HDD class.

### Changed

- The HDD list will now automatically be scanned and populated on program launch.

### Fixed

- The dummy state from the Qt Creator `.ui` file is now reset on program launch, before it's shown.

## [0.0.1] - 2021-10-14

- Initial release only meant as a starting ground for the project structure.
- There is no working logic except for File -> Exit and About options of the Menu Bar.
- Only basic main window layout and appearance has been created so far.

[0.1.0]: https://github.com/rlaphoenix/hdlg/releases/tag/v0.1.0
[0.0.1]: https://github.com/rlaphoenix/hdlg/releases/tag/v0.0.1
