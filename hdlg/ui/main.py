import platform

import pythoncom
import wmi
from PySide2 import QtWidgets, QtGui, QtCore

from hdlg.ui import BaseWindow


class Main(BaseWindow):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

        self.window.setMinimumSize(1000, 400)

        self.window.actionExit.triggered.connect(self.window.close)
        self.window.actionAbout.triggered.connect(self.about)

    def clear_hdd_list(self) -> None:
        """Clear all buttons from the HDD list."""
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                # noinspection PyTypeChecker
                child.setParent(None)

    def add_hdd_button(self, device: wmi._wmi_object) -> None:
        """Add a HDD button into the HDD list. Skips buttons with identical targets."""
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                if child.objectName() == device.DeviceID:
                    return

        button = QtWidgets.QPushButton(f"{device.DeviceID}\n{device.Model}")
        button.setObjectName(device.DeviceID)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        device_list = self.window.deviceListDevices_2.layout()
        device_list.insertWidget(0, button)

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
            self.window.statusbar.showMessage("Scanning HDDs...")

        def on_finish(n: int):
            self.window.refreshIcon.setEnabled(True)
            self.window.statusbar.showMessage("Found %d HDDs" % n)

        def on_error(e: Exception):
            print(e)

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.found_device.connect(self.add_hdd_button)

        self.thread.started.connect(self.worker.find_hdds)
        self.thread.start()


class MainWorker(QtCore.QObject):
    error = QtCore.Signal(Exception)
    finished = QtCore.Signal(int)
    found_device = QtCore.Signal(wmi._wmi_object)

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
                    self.found_device.emit(disk_drive)
                self.finished.emit(len(disk_drives))
            else:
                raise NotImplementedError("Device Scanning has not been implemented for %s." % system)
        except Exception as e:
            self.error.emit(e)
