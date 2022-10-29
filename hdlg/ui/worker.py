from pathlib import Path

import pythoncom
from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QTreeWidgetItem
from wmi import WMI

from hdlg.hdd import HDD
from hdlg.utils import size_unit, hdl_dump_live


class MainWorker(QObject):
    error = Signal(Exception)
    finished = Signal()
    progress = Signal(float)
    status_message = Signal(str)
    found_device = Signal(HDD)
    hdd_info = Signal(list)
    game = Signal(HDD, Path, str, str, str)

    def find_hdds(self) -> None:
        """
        Find Disk Drive devices using WMI on Windows.

        TODO: Add support for Linux and macOS.
        """
        try:
            self.status_message.emit("Scanning HDDs...")
            # noinspection PyUnresolvedReferences
            pythoncom.CoInitialize()  # important!
            c = WMI()
            disk_drives = c.Win32_DiskDrive()
            for disk_drive in sorted(disk_drives, key=lambda d: d.index):
                self.found_device.emit(HDD(
                    target=disk_drive.DeviceID,
                    model=disk_drive.Model
                ))
            self.status_message.emit(f"Found {len(disk_drives)} HDDs")
            self.finished.emit()
        except Exception as e:
            self.error.emit(e)

    def get_hdd_info(self, hdd: HDD) -> None:
        """Get HDD Usage Information like Total/Used/Available Disk Space and a list of Games."""
        try:
            self.status_message.emit(f"Loading HDD %s (%s)" % (hdd.target, hdd.model))
            disk_usage_percent = [
                (hdd.disk_map[1] / hdd.disk_map[0]) * 100,  # Used
                (hdd.disk_map[2] / hdd.disk_map[0]) * 100,  # Available
            ]
            space_tree = QTreeWidgetItem(["Disk Space"])
            space_tree.addChild(QTreeWidgetItem([
                "Total", f"{size_unit(hdd.disk_size)} ({hdd.disk_size})"
            ]))
            space_tree.addChild(QTreeWidgetItem([
                "Used", f"{size_unit(hdd.disk_map[1])} ({hdd.disk_map[1]}, {disk_usage_percent[0]:.2f}%)"
            ]))
            space_tree.addChild(QTreeWidgetItem([
                "Available", f"{size_unit(hdd.disk_map[2])} ({hdd.disk_map[2]}, {disk_usage_percent[1]:.2f}%)"
            ]))

            games = hdd.get_games_list()
            games_tree = QTreeWidgetItem(["Games", str(len(games))])
            for media_type, size, _, dma, game_id, name in games:
                games_tree.addChild(QTreeWidgetItem([
                    f"{media_type} {size_unit(size)} ({dma})",
                    f"{game_id} {name}"
                ]))

            self.hdd_info.emit([
                space_tree,
                games_tree
            ])
            self.status_message.emit(f"Loaded HDD %s (%s)" % (hdd.target, hdd.model))
            self.finished.emit()
        except Exception as e:
            self.error.emit(e)

    def install_game(self, hdd: HDD, iso: Path, media_type: str, disc_label: str, game_id: str):
        """Install a Game ISO to a PS2 HDD."""
        try:
            self.status_message.emit(f"Installing {iso.stem} ({game_id})")
            for line in hdl_dump_live(
                f"inject_{media_type.lower()}",
                hdd.hdl_target, iso.stem.title(), str(iso.absolute()), game_id
            ):
                progress = line.split(", ")
                if len(progress) == 3:
                    progress, remaining, speed = progress
                else:
                    progress, remaining, speed = progress[0], None, None
                self.status_message.emit(", ".join(x for x in [
                    f"{progress} Installed {iso.stem} ({game_id})", remaining, speed
                ] if x))
                progress = float(progress.split("%")[0])
                self.progress.emit(progress)
            self.status_message.emit("Installed %s (%s %s)..." % (disc_label, game_id, media_type))
            self.finished.emit()
        except Exception as e:
            self.error.emit(e)
