from __future__ import annotations

import re
import subprocess
import traceback
from pathlib import Path

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QMessageBox

from hdlg.hdd import HDD
from hdlg.ui import BaseWindow
from hdlg.ui.worker import MainWorker
from hdlg.utils import size_unit, hdl_dump


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
        """Add an HDD button into the HDD list."""
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                # Skip buttons with identical targets
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

            self.window.hddInfoList.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                "\n" * 8 + " " * 90 +
                "Scanning for PS2 HDDs..."
            ]))

        def on_finish():
            self.window.refreshIcon.setEnabled(True)
            self.window.hddInfoList.clear()
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
        self.worker.status_message.connect(self.window.statusbar.showMessage)
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

            if self.window.installButton.isEnabled():
                self.window.installButton.clicked.disconnect()

        def on_finish(_: int):
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.installButton.setEnabled(True)
            self.window.installButton.show()
            self.window.hddInfoList.setEnabled(True)

        def on_error(e: Exception):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Failed to load HDD")
            msg.setText("An error occurred when loading the HDD:")
            msg.setDetailedText(traceback.format_exc())

            error = None
            if isinstance(e, subprocess.CalledProcessError):
                error = e.output.decode()
                if error and "unrecognized command" in error:
                    error = "Unrecognized command, hdl-dump version may be too old."
                elif e.returncode == 107:
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

            self.window.installButton.clicked.connect(lambda: self.install_game(hdd))

        self.thread.started.connect(manage_state)
        self.worker.status_message.connect(self.window.statusbar.showMessage)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.hdd_info.connect(use_hdd_info)

        self.thread.started.connect(lambda: self.worker.get_hdd_info(hdd))
        self.thread.start()

    def install_game(self, hdd: HDD):
        out_dir = QtWidgets.QFileDialog.getOpenFileName(
            self.window,
            "Install PS2 Disc Image (ISO)",
            filter="PS2 ISO (*.ISO);;All files (*.*)",
            # dir=str(cfg.user_cfg.last_opened_directory or "")
        )
        if not out_dir:
            self.log.debug("Cancelled Installation as no PS2 Disc Image (ISO) was provided.")
            return
        out_dir = Path(out_dir[0])

        # TODO: Verify info cdvd_info
        disc_info = hdl_dump("cdvd_info2", str(out_dir))[0]
        disc_info = re.match(r'^([^ ]*) +(\d+)KB +"([^"]*)" +"([^"]+)"', disc_info)
        if not disc_info:
            QMessageBox.information(
                self.window,
                "HDLG",
                f"The ISO file ({out_dir}) does not seem to be a valid PlayStation 2 ISO file, cannot install."
            )
            return
        media_type, game_size, disc_label, game_id = disc_info.groups()
        QMessageBox.information(
            self.window,
            "HDLG",
            "Installation functionality WIP, debug data:\n"
            f"{media_type, game_size, disc_label, game_id}"
        )
