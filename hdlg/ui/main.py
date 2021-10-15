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
