# -*- coding: utf-8 -*-
#
# mimms - mms stream downloader
# Copyright © 2008 Wesley J. Landaker <wjl@icecavern.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module uses ctypes to interface to libmms. Currently, it just
exposes the mmsx interface, since this one is the most flexible.
"""
from sys import platform, exit
from ctypes import *

if platform == "darwin":
    try:
        libmms = cdll.LoadLibrary("libmms.0.dylib")
    except Exception, e:
        print e
        sys.exit("[!!!] ERROR: No se encuentra dependencia: libmms\nhttp://sourceforge.net/projects/libmms/")
elif platform == "win32": # Nunca entrará por aquí, se filtra en Descargar.py antes de entrar aquí (se deja a futuro)
    exit("[!!!] ERROR: libmms aun no disponible en Windows")
    try:
        libmms = cdll.LoadLibrary("libmms/cygmms-0.dll")
    except Exception, e:
        print e
        sys.exit("[!!!] ERROR: No se encuentra dependencia: libmms\nhttp://sourceforge.net/projects/libmms/")
else:
    try:
        libmms = cdll.LoadLibrary("libmms.so.0")
    except Exception, e:
        print e
        sys.exit("[!!!] ERROR: No se encuentra dependencia: libmms\nhttp://sourceforge.net/projects/libmms/")

# opening and closing the stream
libmms.mmsx_connect.argtypes = [c_void_p, c_void_p, c_char_p, c_int]
libmms.mmsx_connect.restype = c_void_p

libmms.mmsx_close.argtypes = [c_void_p]
libmms.mmsx_close.restype = None

# querying length and position
libmms.mmsx_get_current_pos.argtypes = [c_void_p]
libmms.mmsx_get_current_pos.restype = c_longlong

libmms.mmsx_get_length.argtypes = [c_void_p]
libmms.mmsx_get_length.restype = c_uint

libmms.mmsx_get_time_length.argtypes = [c_void_p]
libmms.mmsx_get_time_length.restype = c_double

# seeking
libmms.mmsx_get_seekable.argtypes = [c_void_p]
libmms.mmsx_get_seekable.restype = c_int

libmms.mmsx_seek.argtypes = [c_void_p, c_void_p, c_longlong, c_int]
libmms.mmsx_seek.restype = c_longlong

libmms.mmsx_time_seek.argtypes = [c_void_p, c_void_p, c_double]
libmms.mmsx_time_seek.restype = c_int

# reading data
libmms.mmsx_read.argtypes = [c_void_p, c_void_p, c_char_p, c_int]
libmms.mmsx_read.restype = c_int

class Error(Exception):
  "Encapsulates a libmms error."
  pass

class Stream:
  "Simple class wrapper for libmms using mmsx calls."

  def __init__(self, url, bandwidth):
    "Connect to the given URL, prefering the given bandwidth."
    self.mms = libmms.mmsx_connect(None, None, url, int(bandwidth))
    if not self.mms:
      raise Error("libmms connection error")

  def length(self):
    "Return the length of the stream, in bytes."
    return libmms.mmsx_get_length(self.mms)

  def position(self):
    "Return the current position of the stream, in bytes."
    return libmms.mmsx_get_current_pos(self.mms)

  def duration(self):
    "Return the duration of the stream, in (fractional) seconds."
    return libmms.mmsx_get_time_length(self.mms)

  def seekable(self):
    "Return whether or not the stream is seekable."
    return libmms.mmsx_get_seekable(self.mms)

  def seek(self, pos):
    "Seek to the given position in the stream, in bytes."
    return libmms.mmsx_seek(None, self.mms, pos, 0);

  def time_seek(self, time):
    "Seek to the given time in the stream, in (fractional) seconds."
    return libmms.mmsx_time_seek(None, self.mms, float(time));

  def read(self):
    "Read a block of data from the stream."
    buffer = create_string_buffer(1024)
    count = libmms.mmsx_read(0, self.mms, buffer, 1024)
    if count < 0:
      raise Error("libmms read error")
    return buffer[:count]

  def __iter__(self):
    "Iterate over all the data in the stream."
    while True:
      data = self.read()
      if data:
        yield data
      else:
        break

  def close(self):
    "Close the stream."
    libmms.mmsx_close(self.mms)

