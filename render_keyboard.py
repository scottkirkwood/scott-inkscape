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
import svg_regex

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
  for cur_def in cur_defs.iterchildren(tagname):
    if cur_def.get('id'):
      curIds[cur_def.get('id')] = True

  for new_def in to_merge_defs.iterchildren(tagname):
    if new_def.get('id') not in curIds:
      cur_defs.append(new_def)

class XY:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def set(self, xy):
    self.x = xy.x
    self.y = xy.y
    return self

  def setx(self, xy):
    self.x = xy.x
    return self

  def sety(self, xy):
    self.y = xy.y
    return self

  def trans(self, dx, dy):
    """Translate."""
    self.x += dx
    self.y += dy
    return self

  def transx(self, dx):
    """Translate in x direction."""
    self.x += dx
    return self

  def transy(self, dy):
    """Translate in y direction."""
    self.y += dy
    return self

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

    # Create a new layer.
    self.layer = inkex.etree.SubElement(svg, 'g')
    self.layer.set(addNS('label', 'inkscape'), 'Button layer')
    self.layer.set(addNS('groupmode', 'inkscape'), 'layer')

    self.CreateKeyboard()

  def CreateKeyboard(self):
    xy = XY(10, 10)
   
    key_w, key_h = self.key.key_w, self.key.key_h

    keys = ['Esc', '.', 'F1', 'F2', 'F3', 'F4', '', 'F5', 'F6', 'F7', 'F8', '', 'F9', 'F10', 'F11', 'F12']
    curxy = XY()
    curxy.set(xy)
    for key_let in keys:
      if key_let == '.':
        curxy.transx(key_w)
        continue
      if not key_let:
        curxy.transx(key_w / 2)
        continue
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.transx(key_w / 4)
    for key_let in ['PrtScr', 'Scroll', 'Pause']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.setx(xy)
    curxy.transy(key_h * 1.2)
    keys = '`1234567890-='
    for key_let in keys:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy = self.PositionKey(self.key, curxy, 2.0, 'Back')

    curxy.transx(key_w / 4)
    for key_let in ['Ins', 'Home', 'PgUp']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.transx(key_w / 4)
    for key_let in ['Num', '/', '*', '-']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.setx(xy)
    curxy.transy(key_h)
    tab_w = 1.5
    curxy = self.PositionKey(self.key, curxy, tab_w, 'Tab')
    
    keys = 'QWERTYUIOP[]'
    for key_let in keys:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)
    curxy = self.PositionKey(self.key, curxy, 1.5, '\\')

    curxy.transx(key_w / 4)
    for key_let in ['Del', 'End', 'PgDn']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.transx(key_w / 4)
    for key_let in ['7', '8', '9', '+']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.setx(xy)  # new line
    curxy.transy(key_h)

    curxy = self.PositionKey(self.key, curxy, 2.1, 'Caps')

    keys = 'ASDFGHJKL;\''
    for i, key_let in enumerate(keys):
      curxy = self.PositionKey(self.key, curxy, 0, key_let)
    curxy = self.PositionKey(self.key, curxy, 1.99, 'Enter')
    
    curxy.transx(key_w / 2 + key_w * 3)
    for key_let in ['4', '5', '6']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.setx(xy)  # new line
    curxy.transy(key_h)

    shift_w = 2.49
    curxy = self.PositionKey(self.key, curxy, shift_w, 'Shift')

    keys = 'ZXCVBNM,./'
    for i, key_let in enumerate(keys):
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy = self.PositionKey(self.key, curxy, 2.65, 'Shift')
    
    curxy.transx(key_w / 4 + key_w)
    for key_let in ['^']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.transx(key_w + key_w / 4)
    for key_let in ['1', '2', '3']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.setx(xy)
    curxy.transy(key_h)
    for key_let in ['Ctrl', 'Win', 'Alt']:
      wider = 1.4
      curxy = self.PositionKey(self.key, curxy, wider, key_let)

    space_w = 6
    curxy = self.PositionKey(self.key, curxy, space_w, '')

    for key_let in ['Alt', 'Win', 'Menu', 'Ctrl']:
      wider = 1.282
      curxy = self.PositionKey(self.key, curxy, wider, key_let)

    curxy.transx(key_w / 4)
    for key_let in ['<', 'd', '>']:
      curxy = self.PositionKey(self.key, curxy, 0, key_let)

    curxy.transx(key_w / 4)
    curxy = self.PositionKey(self.key, curxy, 2.1, '0')
    curxy = self.PositionKey(self.key, curxy, 0, '.')


  def PositionKey(self, element, xy, dw, letter):
    """Position, stretch and change the letter after duplicating.
    Args:
      element: the element to duplicate
      xy: Position to move to.
      dw: How much to make wider 0 or 1 means don't change.
      letter: New letter to use in tspan
    """
    cur_key = copy.deepcopy(element.key)
    tspan = cur_key.find('.//' + addNS('tspan', 'svg'))
    tspan.text = letter
    # Set text position to center of document.
    cur_key.set('transform', 'translate(%d,%d)' % (xy.x, xy.y))
    if not dw or dw == 1:
      self.layer.append(cur_key)
      return xy.transx(element.key_w)
    rect = cur_key.find(addNS('rect', 'svg'))
    old_w = inkex.unittouu(rect.get('width'))
    w = old_w * dw
    dx = w - old_w

    rect.set('width', str(w))
    for path in cur_key.iterchildren(addNS('text', 'svg')):
      TranslateXY(path, (dx / 2.0, 0))
      for tspan in path.iterchildren(addNS('tspan', 'svg')):
        TranslateXY(tspan, (dx / 2.0, 0))
    for path in cur_key.iterchildren(addNS('path', 'svg')):
      d = svg_regex.svg_parser.parse(path.get('d'))
      id = path.get('id')
      d2 = TranslatePath(d, (dx, 0), (10, 0))
      path.set('d', d2)
    self.layer.append(cur_key)
    return xy.transx(element.key_w + dx + 0.1 * dw)

def TranslateXY(elem, (dx, dy)):
  """Translate an element by (x, y)."""
  if dx:
    x = inkex.unittouu(elem.get('x'))
    elem.set('x', str(x + dx))
  if dy:
    y = inkex.unittouu(elem.get('y'))
    elem.set('y', str(y + dy))

def TranslatePath(d, (dx, dy), (ifgtx, ifgty)):
  """convert [('M', [(1, 2),(3,4)])] to 'M 2,4 4,6' with (dx=1,dy=1).
  Args:
    d: path ex. [('T', [ (x, y), ]), ('Z', None)]
    dx, dy: delta for x and y direction.
    ifgtx, ifgty: use delta if x or y > this value.
  """
  ret = []
  for op, values in d:
    ret.append(op)
    if values:
      for x, y in values:
        if ifgtx and x > ifgtx:
          x += dx
        if ifgty and y > ifgty:
          y += dy
        ret.append('%f,%f' % (x, y))
  return ' '.join(ret)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()
