#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Scott Kirkwood. All Rights Reserved.

"""Create a seven segment display from a template.

The template needs to be in a certain format:
You should have the segments as paths named with the following IDs

    tc
 tl    tr
    cc
 bl    br
    bc   

The program will delete (remove) the appropriate segments in order to
make a number (0-9).
"""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

import inkex
import logging

addNS = inkex.addNS

SEGMENTS_TO_DELETE = {
  0: ['cc'],
  1: ['tc', 'tl', 'cc', 'bl', 'bc'],
  2: ['tl', 'br'],
  3: ['tl', 'bl'],
  4: ['tc', 'bl', 'bc'],
  5: ['tr', 'bl'],
  6: ['tr'],
  7: ['tl', 'cc', 'bl', 'bc'],
  8: [],
  9: ['bl'],
}

class SevenSegment(inkex.Effect):
  """
  Example Inkscape effect extension.
  """
  def __init__(self):
    """
    Constructor.
    """
    # Call the base class constructor.
    inkex.Effect.__init__(self)

    self.OptionParser.add_option('-n', '--number', action='store', 
      type='int', dest='number', default=0,
      help='Number to create.')

  def effect(self):
    """
    Effect behaviour.
    Create multiple keys.
    """
    # Get access to main SVG document element and get its dimensions.
    svg = self.document.getroot()

    width  = inkex.unittouu(svg.get('width'))
    height = inkex.unittouu(svg.get('height'))

    num = self.options.number
    if num not in SEGMENTS_TO_DELETE:
      logging.error('Number must be between 0 and 9')
      return

    self.DeleteSegments(svg, SEGMENTS_TO_DELETE[num])

  def DeleteSegments(self, root, segments):
    lookup = dict((x, True) for x in segments)
    lookup.update(dict((x + '1', True) for x in segments))
    lookup.update(dict((x + '2', True) for x in segments))
    lookup.update(dict((x + '3', True) for x in segments))
    for g in root.iter(addNS('g', 'svg')):
      for path in g.iterchildren(addNS('path', 'svg')):
        if path.get('id') in lookup:
          g.remove(path)



# Create effect instance and apply it.
effect = SevenSegment()
effect.affect()
