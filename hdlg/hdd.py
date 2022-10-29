"""
hdlg - Modern GUI for hdl-dump.
Copyright (C) 2021-2022 rlaphoenix

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import struct
from ctypes.wintypes import HANDLE
from pathlib import Path
from typing import Union

import win32con
import win32file
import winioctlcon

from hdlg.utils import NEIGHBORING_WHITESPACE, hdl_dump


class HDD:
    def __init__(self, target: Union[str, Path], model: str):
        self.handle = win32file.INVALID_HANDLE_VALUE
        self.target = target
        self.hdl_target = target.upper().replace(r"\\.\PHYSICALDRIVE", "hdd") + ":"
        self.model = model

        self._geometry = None
        self._disk_size = None
        self._disk_map = None
        self._is_apa_partitioned = None
        self._apa_checksum = None

        self.open(target)

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self.dispose()

    def dispose(self):
        if self.handle != win32file.INVALID_HANDLE_VALUE:
            win32file.CloseHandle(self.handle)

    def open(self, device: str, extended=False) -> HANDLE:
        if not device.startswith("\\\\.\\"):
            device = r"\\.\%s" % device  # unc target
        self.handle = win32file.CreateFile(
            # https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea
            device,  # target
            win32con.MAXIMUM_ALLOWED,  # 0x0080 | 0x0020,  # desired access
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,  # share mode
            None,  # security attributes
            win32con.OPEN_EXISTING,  # creation disposition
            win32con.FILE_ATTRIBUTE_NORMAL,  # flags and attributes
            None  # template file
        )
        if self.handle == win32file.INVALID_HANDLE_VALUE:
            raise RuntimeError("Failed to obtain device handle...")
        if extended:
            # TODO: Sometimes works, sometimes doesn't. Only got it working (once) on a CD-ROM drive with a DVD.
            print(win32file.DeviceIoControl(self.handle, winioctlcon.FSCTL_ALLOW_EXTENDED_DASD_IO, None, None))
        return self.handle

    def seek(self, to: int, whence: int = win32file.FILE_BEGIN) -> int:
        pos = win32file.SetFilePointer(self.handle, to, whence)
        if pos != to:
            raise IOError(f"Seek was not precise...")
        return pos

    def read(self, size: int) -> bytes:
        if size % 512 != 0:
            raise ValueError("Size must be a multiple of 512 for some reason, Ask Windows.")
        res, data = win32file.ReadFile(self.handle, size, None)
        if res != 0:
            raise IOError(f"An error occurred: {res} {data}")
        if len(data) < size:
            raise IOError(f"Read {size - len(data)} less bytes than requested...")
        return data

    @property
    def geometry(self) -> tuple[int, ...]:
        """
        Retrieves information about the physical disk's geometry.
        https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-disk_geometry_ex

        Returns a tuple of:
            Cylinders-Lo
            Cylinders-Hi
            Media Type
            Tracks Per Cylinder
            Sectors Per Track
            Bytes Per Sector
            Disk Size
            Extra Data
        """
        if self._geometry is not None:
            return self._geometry

        if self.handle == win32file.INVALID_HANDLE_VALUE:
            raise ValueError("Handle is invalid, have you opened a handle yet?")

        self._geometry = struct.unpack("8L", win32file.DeviceIoControl(
            self.handle,  # handle
            winioctlcon.IOCTL_DISK_GET_DRIVE_GEOMETRY_EX,  # ioctl api
            None,  # in buffer
            32  # out buffer
        ))
        return self._geometry

    @property
    def disk_size(self) -> int:
        """Get full Disk Size (in bytes)."""
        if self._disk_size is not None:
            return self._disk_size

        cyl_lo, cyl_hi, _, tpc, spt, bps, _, _ = self.geometry

        self._disk_size = (cyl_lo + cyl_hi) * tpc * spt * bps
        return self._disk_size

    @property
    def disk_map(self) -> tuple[int, ...]:
        """Get Total Slice Size, Used Space, and Available Space (in bytes)."""
        if self._disk_map is not None:
            return self._disk_map

        disk_map = hdl_dump("map", self.hdl_target)[-1]
        total, used, available = [
            int(x.split(": ")[1][:-2]) * 1000 * 1000
            for x in disk_map.split(", ")
        ]

        self._disk_map = (total, used, available)

        return self._disk_map

    @property
    def is_apa_partitioned(self) -> bool:
        """Check if HDD is a PS2 APA-formatted device."""
        if self._is_apa_partitioned is not None:
            return self._is_apa_partitioned

        old_pos = self.seek(0, whence=win32file.FILE_CURRENT)

        try:
            if self.seek(0) != 0:
                raise RuntimeError("Unable to seek to start of HDD, cannot check if APA Partitioned...")
            header = self.read(1024)
            checksum = header[0:4]
            magic = header[4:8]

            new_checksum = struct.pack(
                "<Q",
                sum(struct.unpack("<I", header[n:n+4])[0] for n in range(4, 1024, 4))
            )[:4]

            self._is_apa_partitioned = magic == b"APA\0" and checksum == new_checksum
        finally:
            self.seek(old_pos)

        return self._is_apa_partitioned

    @property
    def apa_checksum(self):
        if not self.is_apa_partitioned:
            return None

        if self._apa_checksum is not None:
            return self._apa_checksum

        old_pos = self.seek(0, whence=win32file.FILE_CURRENT)

        try:
            if self.seek(0) != 0:
                raise RuntimeError("Unable to seek to start of HDD, cannot get APA checksum...")
            header = self.read(512)
            self._apa_checksum = header[0:4]
        finally:
            self.seek(old_pos)

        return self._apa_checksum

    def get_games_list(self) -> list[tuple[str, int, int, str, str, str]]:
        """
        Get a list of games installed on the HDD (if any).

        Returns a tuple of:
            MediaType
            Size (in Bytes)
            Flags
            DMA
            GameID
            GameName
        """
        # TODO: Add handler for when there's no games installed
        games = hdl_dump("hdl_toc", self.hdl_target)[1:-1]
        # [!] will show as the Game Name for any game that was improperly installed
        games = [
            (NEIGHBORING_WHITESPACE.sub(" ", game).split(" ", maxsplit=5) + ["[!]"])[:6]
            for game in games
        ]
        games = [
            (media_type, int(size.replace("KB", "")) * 1000, int(flags), dma, game_id, game_name)
            for media_type, size, flags, dma, game_id, game_name in games
        ]
        games.sort(key=lambda x: x[-1])
        return games
