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

        self.reset_state()
        self.window.setMinimumSize(1000, 400)
        self.window.hddInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # menu bar actions
        self.window.actionExit.triggered.connect(self.window.close)
        self.window.actionAbout.triggered.connect(self.about)

        # button actions
        self.window.refreshIcon.clicked.connect(self.refresh_hdd_list)

        # store data here to keep in scope and out of garbage collection
        # necessary for the thread and worker class
        self.GC_KEEP = None

        self.refresh_hdd_list()

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

    def reset_state(self) -> None:
        """Reset the State of the UI and Application to the initial startup."""
        # Clear all HDD buttons from the HDD list
        for child in self.window.deviceListDevices_2.children():
            if isinstance(child, QtWidgets.QPushButton):
                # noinspection PyTypeChecker
                child.setParent(None)

        # Reset the HDD information panel
        self.window.hddInfoList.clear()
        self.window.hddInfoList.setEnabled(False)
        self.window.hddInfoList.addTopLevelItem(QtWidgets.QTreeWidgetItem([
            "\n" * 8 + " " * 90 +
            "Scanning for PS2 HDDs..."
        ]))

        # Reset the Installation Button
        self.window.installButton.setEnabled(False)
        self.window.installButton.hide()

        # Reset the Progress Bar
        self.window.progressBar.hide()
        self.window.progressBar.setValue(0)

        # Enable the Refresh Button
        self.window.refreshIcon.setEnabled(True)

    def refresh_hdd_list(self) -> None:
        """Remove list of HDD devices and reload them."""
        self.reset_state()
        self.window.refreshIcon.setEnabled(False)

        thread = QtCore.QThread()
        worker = MainWorker()
        worker.moveToThread(thread)

        def on_finish():
            self.window.refreshIcon.setEnabled(True)
            self.window.hddInfoList.clear()
            self.window.hddInfoList.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                "\n" * 8 + " " * 60 +
                "Ready to go? Just choose a PS2 HDD to get started!"
            ]))
            thread.quit()

        def on_error(e: Exception):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Failed to list HDDs")
            msg.setText("An error occurred when listing HDDs:")
            msg.setDetailedText(traceback.format_exc())
            msg.setInformativeText(str(e))
            msg.exec_()

        worker.finished.connect(on_finish)
        worker.error.connect(on_error)

        worker.status_message.connect(self.window.statusbar.showMessage)
        worker.found_device.connect(self.add_hdd_button)

        thread.started.connect(worker.find_hdds)
        thread.start()

        self.GC_KEEP = (thread, worker)

    def load_hdd(self, hdd: HDD):
        """Load HDD device, get HDD object, get device information."""
        # prevent refreshing of HDDs, loading of an HDD, or installation
        self.window.refreshIcon.setEnabled(False)
        self.window.deviceListDevices_2.setEnabled(False)
        self.window.installButton.hide()
        if self.window.installButton.isEnabled():
            self.window.installButton.clicked.disconnect()

        self.window.hddInfoList.clear()
        self.window.hddInfoList.addTopLevelItem(QtWidgets.QTreeWidgetItem([
            "\n" * 8 + " " * 100 +
            "Loading PS2 HDD..."
        ]))

        thread = QtCore.QThread()
        worker = MainWorker()
        worker.moveToThread(thread)

        def on_finish():
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.installButton.setEnabled(True)
            self.window.installButton.show()
            self.window.hddInfoList.setEnabled(True)
            self.window.installButton.clicked.connect(lambda: self.install_game(hdd))
            thread.quit()

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

        def set_hdd_info(trees: list[QtWidgets.QTreeWidgetItem]):
            self.window.hddInfoList.clear()
            for tree in trees:
                self.window.hddInfoList.addTopLevelItem(tree)
            self.window.hddInfoList.expandToDepth(0)

        worker.finished.connect(on_finish)
        worker.error.connect(on_error)

        worker.status_message.connect(self.window.statusbar.showMessage)
        worker.hdd_info.connect(set_hdd_info)

        thread.started.connect(lambda: worker.get_hdd_info(hdd))
        thread.start()

        self.GC_KEEP = (thread, worker)

    def install_game(self, hdd: HDD):
        iso_path = QtWidgets.QFileDialog.getOpenFileName(
            self.window,
            "Install PS2 Disc Image (ISO)",
            filter="PS2 ISO (*.ISO);;CDRWIN BIN/CUE (*.CUE);;Nero Burning Rom Image (*.NRG);;"
                   "RecordNow! Global Image (*.GI);;Sony CD/DVD Intermediate (*.IML);;All files (*.*)",
            # dir=str(cfg.user_cfg.last_opened_directory or "")
        )
        if not iso_path[0]:
            self.log.debug("Cancelled Installation as no PS2 Disc Image (ISO) was provided.")
            return
        iso_path = Path(iso_path[0])

        # TODO: Verify info cdvd_info
        disc_info = hdl_dump("cdvd_info2", str(iso_path))[0]
        disc_info = re.match(r'^([^ ]*) +(\d+)KB +"([^"]*)" +"([^"]+)"', disc_info)
        if not disc_info:
            QMessageBox.information(
                self.window,
                "HDLG",
                f"The ISO file ({iso_path}) does not seem to be a valid PlayStation 2 ISO file, cannot install."
            )
            return
        media_type, game_size, disc_label, game_id = disc_info.groups()

        self.window.deviceListDevices_2.setEnabled(False)
        self.window.refreshIcon.setEnabled(False)
        self.window.installButton.setEnabled(False)
        self.window.progressBar.show()
        self.window.progressBar.setValue(0)

        thread = QtCore.QThread()
        worker = MainWorker()
        worker.moveToThread(thread)

        def on_progress(n: float):
            self.window.progressBar.setValue(n)

        def on_finish():
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.installButton.setEnabled(True)
            # update disk usage and games list
            self.load_hdd(hdd)
            thread.quit()

        def on_error(e: Exception):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Failed to install Game")
            msg.setText("An error occurred when installing a Game to an HDD:")
            msg.setDetailedText(traceback.format_exc())
            msg.setInformativeText(str(e))
            msg.exec_()

        worker.progress.connect(on_progress)
        worker.finished.connect(on_finish)
        worker.error.connect(on_error)

        worker.status_message.connect(self.window.statusbar.showMessage)

        # TODO: Is there a better way to do this?
        worker.game.connect(worker.install_game)
        thread.started.connect(lambda: worker.game.emit(hdd, iso_path, media_type, disc_label, game_id))
        thread.start()

        self.GC_KEEP = (thread, worker)
