#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

from simplestyle import *
import inkex
import os
import simplepath
import logging

def LoadPath(svg_path):
  """Load an svg file and return it.
  Args:
    svg_path: Svg filename
  Returns:
    first layers, width, height
  """
  extensionDir = os.path.normpath(
                     os.path.join( os.getcwd(), os.path.dirname(__file__) )
                 )
  # __file__ is better then sys.argv[0] because this file may be a module
  # for another one.
  fname = os.path.join(extensionDir, svg_path)
  logging.info('fname: %r' % fname)
  tree = inkex.etree.parse(fname)
  root = tree.getroot()
  g = root.find(inkex.addNS('g', 'svg'))
  if g == None:
    return None, None, 0, 0
  width = root.get("width")
  height = root.get("height")
  defs = root.find(inkex.addNS('defs', 'svg'))
  return g, defs, width, height


class HelloWorldEffect(inkex.Effect):
  """
  Example Inkscape effect extension.
  Creates a new layer with a "Hello World!" text centered in the middle of the document.
  """
  def __init__(self):
    """
    Constructor.
    """
    # Call the base class constructor.
    inkex.Effect.__init__(self)

    # Define string option "--what" with "-w" shortcut and default value "World".
    self.OptionParser.add_option('-k', '--keyfile', action = 'store',
      type = 'string', dest = 'keyfile', default = 'key.svg',
      help = 'The template svg file')

  def effect(self):
    """
    Effect behaviour.
    Create multiple keys.
    """
    # Get access to main SVG document element and get its dimensions.
    svg = self.document.getroot()

    width  = inkex.unittouu(svg.get('width'))
    height = inkex.unittouu(svg.get('height'))

    keyfile = self.options.keyfile
    key, defs, w_key, h_key = LoadPath(keyfile)

    cur_def = svg.find(inkex.addNS('defs', 'svg'))
    for my_def in defs.iter(inkex.addNS('linearGradient', 'svg')):
      cur_def.append(my_def)

    # Create a new layer.
    layer = inkex.etree.SubElement(svg, 'g')
    layer.set(inkex.addNS('label', 'inkscape'), 'Button layer')
    layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

    # Set text position to center of document.
    key.set('transform', 'translate(%d,%d)' % (width / 2, height / 2))

    layer.append(key)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()
