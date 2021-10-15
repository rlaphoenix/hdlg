import platform

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

    def add_hdd_button(self, device: wmi._wmi_object) -> None:
        """Add a HDD button into the HDD list. Skips buttons with identical targets."""
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                if child.objectName() == device.DeviceID:
                    return

        button = QtWidgets.QPushButton(f"{device.DeviceID}\n{device.Model}")
        button.setObjectName(device.DeviceID)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.load_hdd(device))

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

    def load_hdd(self, device: wmi._wmi_object):
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
            self.window.statusbar.showMessage(f"Loading HDD %s (%s)" % (device.DeviceID, device.Model))

            if self.window.installButton.isEnabled():
                self.window.installButton.clicked.disconnect()

        def on_finish(_: int):
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.installButton.setEnabled(True)
            self.window.installButton.show()
            self.window.statusbar.showMessage("Loaded HDD %s (%s)" % (device.DeviceID, device.Model))

        def on_error(e: Exception):
            print("An error occurred somewhere in Main->load_device():", e)

        def use_hdd(hdd: HDD):
            self.window.hddInfoList.clear()
            geometry = QtWidgets.QTreeWidgetItem(["Geometry", str(hdd.get_geometry())])
            self.window.hddInfoList.addTopLevelItem(geometry)

            self.window.hddInfoList.expandToDepth(0)
            self.window.hddInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.hdd.connect(use_hdd)

        self.worker.device.connect(self.worker.load_hdd)
        self.thread.started.connect(lambda: self.worker.device.emit(device))
        self.thread.start()


class MainWorker(QtCore.QObject):
    # input signals
    device = QtCore.Signal(wmi._wmi_object)

    # output signals
    error = QtCore.Signal(Exception)
    finished = QtCore.Signal(int)
    found_device = QtCore.Signal(wmi._wmi_object)
    hdd = QtCore.Signal(HDD)

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

    def load_hdd(self, device: wmi._wmi_object):
        try:
            pythoncom.CoInitialize()
            hdd = HDD(device.DeviceID)
            self.hdd.emit(hdd)
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)
