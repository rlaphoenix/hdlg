from __future__ import annotations

import subprocess
import traceback

import pythoncom
import wmi

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QMessageBox

from hdlg.hdd import HDD
from hdlg.ui import BaseWindow
from hdlg.utils import size_unit


class Main(BaseWindow):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

        self.window.setMinimumSize(1000, 400)
        self.window.installButton.setEnabled(False)
        self.window.installButton.hide()
        self.window.progressBar.hide()
        self.window.hddInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.window.actionExit.triggered.connect(self.window.close)
        self.window.actionAbout.triggered.connect(self.about)
        self.window.refreshIcon.clicked.connect(self.get_hdd_list)

        self.get_hdd_list()

    def clear_hdd_list(self) -> None:
        """Clear all buttons from the HDD list."""
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                # noinspection PyTypeChecker
                child.setParent(None)

    def add_hdd_button(self, hdd: HDD) -> None:
        """Add a HDD button into the HDD list. Skips buttons with identical targets."""
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                if child.objectName() == hdd.target:
                    return

        button = QtWidgets.QPushButton("\n".join([
            " ".join([
                hdd.hdl_target,
                f"({size_unit(hdd.disk_size)}" + [")", ", PS2)"][hdd.is_apa_partitioned]
            ]),
            hdd.model
        ]))
        button.setObjectName(hdd.target)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setEnabled(hdd.is_apa_partitioned)
        button.setCheckable(hdd.is_apa_partitioned)
        button.clicked.connect(lambda: self.load_hdd(hdd))
        button.toggled.connect(lambda: button.setChecked(True))

        device_list = self.window.deviceListDevices_2.layout()
        device_list.insertWidget(0 if hdd.is_apa_partitioned else device_list.count() - 1, button)

    def get_hdd_list(self) -> None:
        """Finds HDD devices and adds them to the HDD list."""
        self.thread = QtCore.QThread()
        self.worker = MainWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.window.refreshIcon.setEnabled(False)
            self.window.installButton.hide()
            self.window.hddInfoList.clear()
            self.window.hddInfoList.setEnabled(False)
            self.clear_hdd_list()
            self.window.statusbar.showMessage("Scanning HDDs...")

            self.window.hddInfoList.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                "\n" * 8 + " " * 90 +
                "Scanning for PS2 HDDs..."
            ]))

        def on_finish(n: int):
            self.window.refreshIcon.setEnabled(True)
            self.window.hddInfoList.clear()
            self.window.statusbar.showMessage("Found %d HDDs" % n)

            self.window.hddInfoList.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                "\n" * 8 + " " * 60 +
                "Ready to go? Just choose a PS2 HDD to get started!"
            ]))

        def on_error(e: Exception):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Failed to list HDDs")
            msg.setText("An error occurred when listing HDDs:")
            msg.setDetailedText(traceback.format_exc())
            msg.setInformativeText(str(e))
            msg.exec_()

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.found_device.connect(self.add_hdd_button)

        self.thread.started.connect(self.worker.find_hdds)
        self.thread.start()

    def load_hdd(self, hdd: HDD):
        """Load HDD device, get HDD object, get device information."""
        self.thread = QtCore.QThread()
        self.worker = MainWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.window.deviceListDevices_2.setEnabled(False)
            self.window.refreshIcon.setEnabled(False)
            self.window.installButton.hide()
            self.window.hddInfoList.clear()
            self.window.statusbar.showMessage(f"Loading HDD %s (%s)" % (hdd.target, hdd.model))

            if self.window.installButton.isEnabled():
                self.window.installButton.clicked.disconnect()

        def on_finish(_: int):
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.installButton.setEnabled(True)
            self.window.installButton.show()
            self.window.hddInfoList.setEnabled(True)
            self.window.statusbar.showMessage("Loaded HDD %s (%s)" % (hdd.target, hdd.model))

        def on_error(e: Exception):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Failed to load HDD")
            msg.setText("An error occurred when loading the HDD:")
            msg.setDetailedText(traceback.format_exc())

            error = None
            if isinstance(e, subprocess.CalledProcessError):
                error = e.output
                if e.returncode == 107:
                    error = "APA partition is broken"

            if error:
                msg.setInformativeText(error)
            else:
                msg.setInformativeText(str(e))

            msg.exec_()

        def use_hdd_info(trees: list[QtWidgets.QTreeWidgetItem]):
            self.window.hddInfoList.clear()
            for tree in trees:
                self.window.hddInfoList.addTopLevelItem(tree)

            self.window.hddInfoList.expandToDepth(0)

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.hdd_info.connect(use_hdd_info)

        self.thread.started.connect(lambda: self.worker.get_hdd_info(hdd))
        self.thread.start()


class MainWorker(QtCore.QObject):
    error = QtCore.Signal(Exception)
    finished = QtCore.Signal(int)
    found_device = QtCore.Signal(HDD)
    hdd_info = QtCore.Signal(list)

    def find_hdds(self) -> None:
        """Find Disk Drive devices using WMI on Windows."""
        try:
            # noinspection PyUnresolvedReferences
            pythoncom.CoInitialize()  # important!
            c = wmi.WMI()
            disk_drives = c.Win32_DiskDrive()
            for disk_drive in sorted(disk_drives, key=lambda d: d.index):
                self.found_device.emit(HDD(
                    target=disk_drive.DeviceID,
                    model=disk_drive.Model
                ))
            self.finished.emit(len(disk_drives))
        except Exception as e:
            self.error.emit(e)

    def get_hdd_info(self, hdd: HDD) -> None:
        try:
            disk_usage_percent = [
                (hdd.disk_map[1] / hdd.disk_map[0]) * 100,  # Used
                (hdd.disk_map[2] / hdd.disk_map[0]) * 100,  # Available
            ]
            space_tree = QtWidgets.QTreeWidgetItem(["Disk Space"])
            space_tree.addChild(QtWidgets.QTreeWidgetItem([
                "Total", f"{size_unit(hdd.disk_size)} ({hdd.disk_size})"
            ]))
            space_tree.addChild(QtWidgets.QTreeWidgetItem([
                "Used", f"{size_unit(hdd.disk_map[1])} ({hdd.disk_map[1]}, {disk_usage_percent[0]:.2f}%)"
            ]))
            space_tree.addChild(QtWidgets.QTreeWidgetItem([
                "Available", f"{size_unit(hdd.disk_map[2])} ({hdd.disk_map[2]}, {disk_usage_percent[1]:.2f}%)"
            ]))

            games = hdd.get_games_list()
            games_tree = QtWidgets.QTreeWidgetItem(["Games", str(len(games))])
            for media_type, size, _, dma, game_id, name in games:
                games_tree.addChild(QtWidgets.QTreeWidgetItem([
                    f"{media_type} {size_unit(size)} ({dma})",
                    f"{game_id} {name}"
                ]))

            self.hdd_info.emit([
                space_tree,
                games_tree
            ])
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)
