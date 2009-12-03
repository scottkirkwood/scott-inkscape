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
import copy

addNS = inkex.addNS

class Key:
  def __init__(self, fname):
    self.keyfile = fname
    self.key, self.key_defs, self.key_w, self.key_h = LoadPath(self.keyfile)

  def AddDefs(self, defs):
    MergeById(defs, self.key_defs, addNS('linearGradient', 'svg'))

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
  g = root.find(addNS('g', 'svg'))
  is_layer = g.get(addNS('groupmode', 'inkscape'))
  if is_layer == 'layer':
    # If our object has a layer, remove it.
    g = g.find(addNS('g', 'svg'))
  if g == None:
    return None, None, 0, 0
  width  = inkex.unittouu(root.get('width'))
  height = inkex.unittouu(root.get('height'))
  defs = root.find(addNS('defs', 'svg'))
  return g, defs, width, height

def MergeById(cur_defs, to_merge_defs, tagname):
  """Merge defs into cur_defs, filtering on tagname.
  Uses the ids in to_merge_defs to check for uniqueness.
  Args:
    cur_defs: tree we need to iterator over and will add to.
    to_merge_defs: tree we want to add.
    tagname: tag name we will filter on
  """
  curIds = {}
  for cur_def in cur_defs.iter(tagname):
    if cur_def.get('id'):
      curIds[cur_def.get('id')] = True

  for new_def in to_merge_defs.iter(tagname):
    if new_def.get('id') not in curIds:
      cur_defs.append(new_def)

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

    cur_defs = svg.find(addNS('defs', 'svg'))
    self.key = Key('key.svg')
    self.key.AddDefs(cur_defs)
    self.wide = Key('wide.svg')
    self.wide.AddDefs(cur_defs)

    # Create a new layer.
    self.layer = inkex.etree.SubElement(svg, 'g')
    self.layer.set(addNS('label', 'inkscape'), 'Button layer')
    self.layer.set(addNS('groupmode', 'inkscape'), 'layer')

    self.CreateKeyboard()

  def CreateKeyboard(self):
    y = 10
    x = 10
   
    key_w = self.key.key_w
    key_h = self.key.key_h 

    keys = ['Esc', '', 'F1', 'F2', 'F3', 'F4', '', 'F5', 'F6', 'F7', 'F8', '', 'F9', 'F10', 'F11', 'F12']
    cur_x = x
    for key_let in keys:
      if not key_let:
        cur_x += key_w / 2
        continue
      self.PositionKey(self.key, cur_x, y, key_let)
      cur_x += key_w

    cur_x = x
    y += key_h * 1.2
    keys = '`1234567890-='
    for key_let in keys:
      self.PositionKey(self.key, cur_x, y, key_let)
      cur_x += key_w

    x += key_w * 1.50 
    cur_x = x
    y += key_h
    keys = 'QWERTYUIOP[]'
    for key_let in keys:
      self.PositionKey(self.key, cur_x, y, key_let)
      cur_x += key_w

    x += key_w * 0.50 
    cur_x = x
    y += key_h
    keys = 'ASDFGHJKL;\''
    for i, key_let in enumerate(keys):
      self.PositionKey(self.key, cur_x, y, key_let)
      cur_x += key_w

    x += key_w * 0.50 
    cur_x = x
    y += key_h
    keys = 'ZXCVBNM,./'
    for i, key_let in enumerate(keys):
      self.PositionKey(self.key, cur_x, y, key_let)
      cur_x += key_w

    x -= key_w * 2.5
    cur_x = x
    y += key_h
    for key_let in ['Ctrl', 'Win', 'Alt']:
      self.PositionKey(self.wide, cur_x, y, key_let)
      cur_x += self.wide.key_w

  def PositionKey(self, element, x, y, letter):
    cur_key = copy.deepcopy(element.key)
    tspan = cur_key.find('.//' + addNS('tspan', 'svg'))
    tspan.text = letter
    # Set text position to center of document.
    cur_key.set('transform', 'translate(%d,%d)' % (x, y))
    self.layer.append(cur_key)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()
