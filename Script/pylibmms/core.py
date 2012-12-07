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
This module contains the core implementation of mimms. This exists
primarily to make it easier to use mimms from other python programs.
"""

import os
import sys

from optparse import OptionParser
from time import time
from urlparse import urlparse

import libmms

VERSION="3.2"

class Timeout(Exception):
  "Raised when a user-defined timeout has occurred."
  pass

class NotResumeableError(Exception):
  "Raised when a resume is attempted on a non-resumeable stream."
  pass

class Timer:
  "A simple elapsed time timer."

  def __init__(self):
    "Create and start a timer."
    self.start = time()

  def restart(self):
    "Restart the timer, returning the elapsed time since the last start."
    elapsed = self.elapsed()
    self.start = time()
    return elapsed

  def elapsed(self):
    "Return the elapsed time since the last start."
    return time() - self.start

def bytes_to_string(bytes):
  "Given a number of bytes, return a string representation."
  if   bytes < 0:   return "∞ B"
  if   bytes < 1e3: return "%.2f B"  % (bytes)
  elif bytes < 1e6: return "%.2f kB" % (bytes/1e3)
  elif bytes < 1e9: return "%.2f MB" % (bytes/1e6)
  else:             return "%.2f GB" % (bytes/1e9)

def seconds_to_string(seconds):
  "Given a number of seconds, return a string representation."
  if seconds < 0: return "∞ s"

  h = seconds // 60**2
  m = (seconds % 60**2) // 60
  s = seconds % 60
  return "%02d:%02d:%02d" % (h, m ,s)

def get_filename(options):
  "Based on program options, choose an appropriate filename."

  # if we are given a filename, use it; otherwise, synthesize from url
  if options.filename: filename = options.filename
  else:
    filename = os.path.basename(urlparse(options.url).path)
    # assume .wmv if there is no extention
    if filename.find(".") == -1: filename += ".wmv"

  # if we are clobbering or resuming a file, use the filename directly
  if options.clobber or options.resume: return filename

  # otherwise, we need to pick a new filename that isn't used
  new_filename = filename
  i = 1
  while os.path.exists(new_filename):
    new_filename = "%s.%d" % (filename, i)
    i += 1
  return new_filename

def download(options):
  "Using the given options, download the stream to a file."

  #status = "Connecting ..."
  status = "[ Conectando ... ]" 
  if not options.quiet: print status,
  sys.stdout.flush()  

  stream = libmms.Stream(options.url, options.bandwidth)

  if options.resume:
    if not stream.seekable():
      raise NotResumeableError

  filename = get_filename(options)
  if options.resume:
    f = open(filename, "a")
    stream.seek(f.tell())
  else:
    f = open(filename, "w")

  clear = " " * len(status)
  status = "[  Origen  ] %s\n[ Destino  ] %s" % (options.url, filename)
  if not options.quiet: print "\r", clear, "\r", status
  sys.stdout.flush()  

  timeout_timer  = Timer()
  duration_timer = Timer()

  bytes_in_duration = 0
  bytes_per_second  = 0

  for data in stream:
    f.write(data)

    # keep track of the number of bytes handled in the current duration
    bytes_in_duration += len(data)

    # every duration, update progress bar
    if duration_timer.elapsed() >= 1:

      # calculate a weighted average over 10 durations
      bytes_per_second *= 9;
      bytes_per_second += bytes_in_duration / duration_timer.restart()
      bytes_per_second /= 10.0

      # reset the byte counter to prepare for the next duration
      bytes_in_duration = 0

      # estimate the number of seconds remaining
      bytes_remaining = stream.length() - stream.position()
      seconds_remaining = bytes_remaining / bytes_per_second

      # if the stream has no duration, then we can't tell the stream length
      # or estimate the download time remaining
      # TODO: is this always true? is duration 0 iff length is undefined?
      if stream.duration():
        length    = stream.length()
        remaining = seconds_remaining
      else:
        length    = -1
        remaining = -1

      # if we are running with a user-defined timeout, we always have an
      # upper bound on how much time is remaining
      if options.time:
        if remaining < 0 or options.time < remaining:
          remaining = options.time*60 - timeout_timer.elapsed()

      clear = " " * len(status)
      status = "%s / %s (%s/s, Tiempo restante: %s)" % (
        bytes_to_string(stream.position()),
        bytes_to_string(length),
        bytes_to_string(bytes_per_second),
        seconds_to_string(remaining)
        )

      if not options.quiet: print "\r", clear, "\r", status,
      sys.stdout.flush()

      if options.time and timeout_timer.elapsed() > (options.time*60):
        raise Timeout

  f.close()
  stream.close()

def run(argv):
  "Run the main mimms program with the given command-line arguments."

  usage = "usage: %prog [options] <url> [filename]"
  parser = OptionParser(
    usage=usage,
    version=("%%prog %s" % VERSION),
    description="mimms is an mms (e.g. mms://) stream downloader")
  parser.add_option(
    "-c", "--clobber",
    action="store_true", dest="clobber",
    help="automatically overwrite an existing file")
  parser.add_option(
    "-r", "--resume",
    action="store_true", dest="resume",
    help="attempt to resume a partially downloaded stream")
  parser.add_option(
    "-b", "--bandwidth",
    type="float", dest="bandwidth",
    help="the desired bandwidth for stream selection in BANDWIDTH bytes/s")
  parser.add_option(
    "-t", "--time",
    type="int", dest="time",
    help="stop downloading after TIME minutes")
  parser.add_option(
    "-v", "--verbose",
    action="store_true", dest="verbose",
    help="print verbose debug messages to stderr")
  parser.add_option(
    "-q", "--quiet",
    action="store_true", dest="quiet",
    help="don't print progress messages to stdout")
  
  parser.set_defaults(time=0, bandwidth=1e6)
  (options, args) = parser.parse_args(argv)
  if len(args) < 1:
    parser.error("url must be specified")
  elif not args[0].startswith("mms"):
    # TODO: handle http:// urls to .asx files that contain mms urls
    parser.error("only mms urls (i.e. mms://, mmst://, mmsh://) are supported")
  elif len(args) > 2:
    parser.error("unknown extra arguments: %s" % ' '.join(args[2:]))
  
  options.url = args[0]
  if len(args) >= 2: options.filename = args[1]
  else: options.filename = None
    
  try:
    download(options)
  except Timeout:
    if not options.quiet:
      print
      print "Download stopped after user-specified timeout."
  except NotResumeableError:
    if not options.quiet:
      print
    print >> sys.stderr, "Non-seekable streams cannot be resumed."
  except KeyboardInterrupt:
    if not options.quiet:
      print
    print >> sys.stderr, "Descarga abortada por el uasuario. Bye!"
  except libmms.Error, e:
    print >> sys.stderr, "libmms error:", e.message
  else:
    if not options.quiet:
      print
      print "[INFO] Descarga con libmms completada"
