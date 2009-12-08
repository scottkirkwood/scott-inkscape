#!/usr/bin/python
#

"""Simple class to hold the x and y position."""

__author__ = 'scott@forusers.com (Scott Kirkwood))'


class XY:
  """Combine the x and y values into one class."""
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def set(self, xy):
    self.x = xy.x
    self.y = xy.y
    return self

  def setx(self, xy):
    if isinstance(xy, XY):
      self.x = xy.x
    else:
      self.x = xy
    return self

  def sety(self, xy):
    if isinstance(xy, XY):
      self.y = xy.y
    else:
      self.y = xy
    return self

  def trans(self, xy):
    self.x += xy.x
    self.y += xy.y

  def trans(self, dx, dy):
    """Translate."""
    self.x += dx
    self.y += dy
    return self

  def transx(self, dx):
    """Translate in x direction."""
    if isinstance(dx, XY):
      self.x += dx.x
    else:
      self.x += dx
    return self

  def transy(self, dy):
    """Translate in y direction."""
    if isinstance(dy, XY):
      self.y += dy.y
    else:
      self.y += dy
    return self

