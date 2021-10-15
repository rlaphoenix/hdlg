"""
hdlg - Modern cross-platform GUI for hdl-dump.
Copyright (C) 2021 rlaphoenix

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

import struct
import sys
from ctypes.wintypes import HANDLE
from pathlib import Path
from typing import Union

import win32con
import win32file
import winioctlcon


class HDD:
    def __init__(self, target: Union[str, Path]):
        self.handle = win32file.INVALID_HANDLE_VALUE

        self.open(target)

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self.dispose()

    def dispose(self):
        if self.handle != win32file.INVALID_HANDLE_VALUE:
            win32file.CloseHandle(self.handle)

    def open(self, device: str, extended=False) -> HANDLE:
        if sys.platform == "win32":
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
        res, data = win32file.ReadFile(self.handle, size, None)
        if res != 0:
            raise IOError(f"An error occurred: {res} {data}")
        if len(data) < size:
            raise IOError(f"Read {size - len(data)} less bytes than requested...")
        return data

    def get_geometry(self) -> tuple[int, ...]:
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
        if self.handle == win32file.INVALID_HANDLE_VALUE:
            raise ValueError("Handle is invalid, have you opened a handle yet?")
        return struct.unpack("8L", win32file.DeviceIoControl(
            self.handle,  # handle
            winioctlcon.IOCTL_DISK_GET_DRIVE_GEOMETRY_EX,  # ioctl api
            b"",  # in buffer
            32  # out buffer
        ))
