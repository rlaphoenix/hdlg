# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2022-10-29

### Added

- Added support for Python 3.10.
- The CI/CD GitHub Actions workflows were updated and improved.
  Windows Installers are now created automatically.
- Added ability to install any file-based PS2 game file to a PS2 HDD with the 'Install' button.
  Batch installation is supported by selecting multiple game files in the Open File Dialogue.
- Added is_admin(), is_frozen(), and require_admin() utilities.
- Added hdl_dump() utility for executing hdl_dump and returning the stdout.
- The about menu now shows if you are running under a Frozen Python environment.
- HDD now has a `hdl_target` property structured for use with hdl_dump. E.g., `hdd4:` instead of `\\.\E:`.
- HDD now has a cached `disk_map` property that returns the Total Slice Size, Used Space, and Available Space.
- Disk Space is now shown in the HDD Information Panel using the HDD disk_map property.
- HDD buttons now display a 2-pixel border on the left when clicked to indicate which one was loaded.
- UI now uses a `status_message` string signal from the Worker class to update the status bar's message.
- Added a reset_state() method to the UI class to reset the state of the program as if it just opened.
  It's now also being run on start up to remove dummy state data from the Qt Creator `.ui` file.
- The Installation Button now has File Type filters for all supported file-based PS2 game extensions.
- Banner Artwork PNG and PSD, as well as a GitHub Social Banner PSD.
- Recommended hdl-dump and LaunchELF programs are now linked in the README.
- A UI preview image has been added to the README.
- Added an Inno Setup script file to create a Setup binary to install a Frozen Python build.
  It expects a Frozen Python build directory and not a single packed binary.
- Created a Changelog with all previous releases' missing changes.

### Changed

- Administrator Rights are now required when starting due to some low-level calls requiring Administrator permissions.
  This may change over time if alternative methods are found, but for now it is simply required.
- Worker class has been moved to worker.py.
- Games are now sorted alphabetically by Game Name in HDDs get_games_list().
- HDDs are now listed in ascending order based on HDD index.
- Unexpected Errors now open an error dialog with extended error information instead of printing to stdout.
- Replaced manual calls to hdl_dump with the hdl_dump() utility across the codebase.
- HDDs hdl_target property is now used across the codebase instead of manual efforts to calculate the target.
- Worker Class's finished signal is now valueless.
- Various QSS changes were made to improve the UI color scheme.
- Project Development Status changed to Stage 3 - Alpha.

### Removed

- Dropped support for Python 3.6.
- Dropped notion of 'Cross-Platform' across the project as it is not yet cross-platform. Only Windows is currently
  supported and all code that ran only under specific IF trees have been removed and Windows is now expected.
  Support for other Operating Systems will be added in the future.
- 'Looking for Artwork' section in the README has been removed. I'm not specifically looking for any artwork anymore.
- The clear_hdd_list() function has been removed. The new reset_state() function should be used instead as it clears
  more related state information in similar scenarios.

### Fixed

- Unexpected Errors are now caught and handled in the UI thread.
- Unknown Command errors on hdl-dump calls are now explicitly handled telling the user their binary may be outdated.
- Cancelling the Open PS2 Game File Dialogue no longer causes a runtime error.
- HDDs get_games_list() now supports listing improperly installed games where either the game name or id is missing.
  A `[!]` will be shown in place of the missing value to indicate a bad installation.

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

[0.2.0]: https://github.com/rlaphoenix/hdlg/releases/tag/v0.2.0
[0.1.0]: https://github.com/rlaphoenix/hdlg/releases/tag/v0.1.0
[0.0.1]: https://github.com/rlaphoenix/hdlg/releases/tag/v0.0.1
