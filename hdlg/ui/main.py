import platform
from typing import List

import pythoncom
import wmi
from PySide2 import QtWidgets, QtGui, QtCore

from hdlg.hdd import HDD
from hdlg.ui import BaseWindow


class Main(BaseWindow):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

        self.window.setMinimumSize(1000, 400)
        self.clear_hdd_list()  # clear example HDD buttons
        self.window.installButton.setEnabled(False)
        self.window.installButton.hide()
        self.window.progressBar.hide()

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
            hdd.target + (" (PS2)" if hdd.is_apa_partitioned else ""),
            hdd.model
        ]))
        button.setObjectName(hdd.target)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setEnabled(hdd.is_apa_partitioned)
        button.clicked.connect(lambda: self.load_hdd(hdd))

        device_list = self.window.deviceListDevices_2.layout()
        device_list.insertWidget(0 if hdd.is_apa_partitioned else device_list.count() - 1, button)

    def get_hdd_list(self) -> None:
        """Finds HDD devices and adds them to the HDD list."""
        self.clear_hdd_list()

        self.thread = QtCore.QThread()
        self.worker = MainWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.window.refreshIcon.setEnabled(False)
            self.window.installButton.hide()
            self.window.statusbar.showMessage("Scanning HDDs...")

        def on_finish(n: int):
            self.window.refreshIcon.setEnabled(True)
            self.window.statusbar.showMessage("Found %d HDDs" % n)

        def on_error(e: Exception):
            print("An error occurred somewhere in Main->get_hdd_list():", e)

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
            self.window.statusbar.showMessage(f"Loading HDD %s (%s)" % (hdd.target, hdd.model))

            if self.window.installButton.isEnabled():
                self.window.installButton.clicked.disconnect()

        def on_finish(_: int):
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.installButton.setEnabled(True)
            self.window.installButton.show()
            self.window.statusbar.showMessage("Loaded HDD %s (%s)" % (hdd.target, hdd.model))

        def on_error(e: Exception):
            print("An error occurred somewhere in Main->load_device():", e)

        def use_hdd_info(trees: List[QtWidgets.QTreeWidgetItem]):
            self.window.hddInfoList.clear()
            for tree in trees:
                self.window.hddInfoList.addTopLevelItem(tree)

            self.window.hddInfoList.expandToDepth(0)
            self.window.hddInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

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
        """Find Disk Drive devices using win32 api on Windows, or lsscsi on Linux."""
        try:
            # TODO: Filter only PS2 APA-formatted HDDs, Support Linux and macOS
            system = platform.system()
            if system == "Windows":
                # noinspection PyUnresolvedReferences
                pythoncom.CoInitialize()  # important!
                c = wmi.WMI()
                disk_drives = c.Win32_DiskDrive()
                for disk_drive in sorted(disk_drives, key=lambda d: d.index, reverse=True):
                    self.found_device.emit(HDD(
                        target=disk_drive.DeviceID,
                        model=disk_drive.Model
                    ))
                self.finished.emit(len(disk_drives))
            else:
                raise NotImplementedError("Device Scanning has not been implemented for %s." % system)
        except Exception as e:
            self.error.emit(e)

    def get_hdd_info(self, hdd: HDD) -> None:
        try:
            self.hdd_info.emit([
                QtWidgets.QTreeWidgetItem(["APA Checksum", hdd.apa_checksum]),
                QtWidgets.QTreeWidgetItem(["Geometry", str(hdd.get_geometry())])
            ])
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)
