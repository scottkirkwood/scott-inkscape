#!/usr/bin/python
#

"""Map scan codes to key names."""

__author__ = 'scott@forusers.com (Scott Kirkwood))'

import codecs
import os
import re

class ScanCodes:
  def __init__(self):
    self.extension_dir = os.path.normpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))

  def Load(self, fname):
    self.map = self.ReadKdb(os.path.join(self.extension_dir, fname))

  def GetChr(self, scancode):
    return self.map[scancode][1]

  def ReadKdb(self, fname):
    return self.ParseKdb(codecs.open(fname, 'r', 'utf-8').read())

  def ParseKdb(self, text):
    re_line = re.compile(r'(\d+) (\S+) (\S+)\s?(\S*)')
    ret = {}
    for line in text.split('\n'):
      if not line:
        continue
      grps = re_line.search(line)
      if grps:
        ret[int(grps.group(1))] = (grps.group(2), grps.group(3), grps.group(4))
    return ret

