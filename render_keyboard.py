#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

from simplestyle import *
from xy import XY
import copy
import inkex
import logging
import os
import simplepath
import scancodes
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
  extension_dir = os.path.normpath(
      os.path.join(os.getcwd(), os.path.dirname(__file__)))
  # __file__ is better then sys.argv[0] because this file may be a module
  # for another one.
  fname = os.path.join(extension_dir, svg_path)
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
    self.extension_dir = os.path.normpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    self.scancodes = scancodes.ScanCodes()
    self.scancodes.Load('us.kbd')
    self.keys = []

    # Define string option "--what" with "-w" shortcut and default value "World".
    self.OptionParser.add_option('-k', '--keyfile', action='store',
      type='string', dest='keyfile', default='key.svg',
      help='The template svg file')
    self.OptionParser.add_option('-f', '--fkeys', action='store',
      type='string', dest='fkeys', default='true',
      help='Display the Escape and Function keys?')
    self.OptionParser.add_option('-c', '--center_keys', action='store', 
      type='string', dest='center_keys', default='true',
      help='Display the Center keys (Home, Ins, Pgup, etc.)?')
    self.OptionParser.add_option('-n', '--numpad', action='store', 
      type='string', dest='numpad', default='true',
      help='Display the Numeric Keypad?')

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
    self.FixBooleanOption('fkeys')
    self.FixBooleanOption('center_keys')
    self.FixBooleanOption('numpad')
    self.key = Key('key.svg')
    self.key.AddDefs(cur_defs)

    # Create a new layer.
    self.layer = inkex.etree.SubElement(svg, 'g')
    self.layer.set(addNS('label', 'inkscape'), 'Button layer')
    self.layer.set(addNS('groupmode', 'inkscape'), 'layer')

    self.CreateKeyboard()
    self.DumpKeys()

  def FixBooleanOption(self, name):
    """Silly inkscape, doesn't do Booleans properly.
    This fixes it by setting a variable with the same name as the option.
    """
    val = getattr(self.options, name)
    if val.lower() == 'false':
      setattr(self, name, False)
    else:
      setattr(self, name, True)

  def DumpKeys(self):
    fo = open(os.path.join(self.extension_dir, 'key_positions.py'), 'w')
    fo.write('#!/usr/bin/python\n')
    fo.write('# Dump of the key layout from render_keyboard.py\n')
    fo.write('# Scancode: (x, y, w, h)\n')
    fo.write('KEY_POSITIONS = {\n')
    self.keys.sort()
    for key in self.keys:
      fo.write('    %d: (%d, %d, %d, %d),\n' % (key[0], key[1], key[2], key[3], key[4]))
    fo.write('}\n')
    fo.close()


  def CreateKeyboard(self):
    xy = XY(0, 0)
    no_resize = XY(1, 1) 
    key_w, key_h = self.key.key_w, self.key.key_h
    homepadxy = XY(xy.x + key_w * 15.2, 0)
    numpadxy = XY(xy.x + key_w * 18.4, key_h * 1.2)
    
    curxy = XY(0, 0)
    self.TopRow(xy)
    self.NumPad(xy, numpadxy)
    self.CenterPad(homepadxy)

    curxy.setx(xy)
    curxy.transy(key_h * 1.2)

    # Backquote to backspace
    keys = [41, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    for key_let in keys:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy = self.PositionKey(self.key, curxy, XY(2.0, 1), 14)


    curxy.setx(xy)
    curxy.transy(key_h)
    tab_w = 1.5
    curxy = self.PositionKey(self.key, curxy, XY(tab_w, 1), 15)
    
    # Tab, Q-P to backslash
    keys = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
    for key_let in keys:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    curxy = self.PositionKey(self.key, curxy, XY(1.5, 1), 43)

    curxy.setx(xy)  # new line
    curxy.transy(key_h)

    curxy = self.PositionKey(self.key, curxy, XY(2.1, 1), 58)

    # Capslock to A-' to Enter
    keys = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    for i, key_let in enumerate(keys):
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    curxy = self.PositionKey(self.key, curxy, XY(1.99, 1), 28)
    
    curxy.setx(xy)  # new line
    curxy.transy(key_h)

    shift_w = 2.48
    curxy = self.PositionKey(self.key, curxy, XY(shift_w, 1), 42)

    # Shift, Z-M to /
    keys = [44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
    for i, key_let in enumerate(keys):
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    # Right shift
    curxy = self.PositionKey(self.key, curxy, XY(2.65, 1), 54)
    
    curxy.setx(xy)
    curxy.transy(key_h)
    # Ctrl, win, Alt
    for key_let in [29, 125, 56]:
      wider = 1.4
      curxy = self.PositionKey(self.key, curxy, XY(wider, 1), key_let)

    # Space
    space_w = 6
    curxy = self.PositionKey(self.key, curxy, XY(space_w, 1), 57)

    # Alt, Win, Menu, Ctrl
    for key_let in [84, 126, 127, 97]:
      wider = 1.282
      curxy = self.PositionKey(self.key, curxy, XY(wider, 1), key_let)


  def TopRow(self, xy):
    if not self.fkeys:
      return
    no_resize = XY(1, 1) 
    key_w, key_h = self.key.key_w, self.key.key_h

    # Function keys
    keys = [1, '.', 59, 60, 61, 62, '', 63, 64, 65, 66, '', 67, 68, 87, 88]
    curxy = XY()
    curxy.set(xy)
    for key_let in keys:
      if key_let == '.':
        curxy.transx(key_w)
        continue
      if not key_let:
        curxy.transx(key_w / 2)
        continue
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)


  def NumPad(self, xy, numpadxy):
    if not self.numpad:
      return

    no_resize = XY(1, 1) 
    key_w, key_h = self.key.key_w, self.key.key_h
    curxy = XY()
    curxy.set(numpadxy)

    # NumLock to Keypad -
    for key_let in [69, 98, 55, 74]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(numpadxy)
    curxy.transy(key_h)
    # 7 to 9
    for key_let in [71, 72, 73]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
   
    # Plus 
    curxy = self.PositionKey(self.key, curxy, XY(1, 2.06), 78)

    curxy.setx(numpadxy)
    curxy.transy(key_h)
    # 4-5
    for key_let in [75, 76, 77]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(numpadxy)
    curxy.transy(key_h)
    # 1-3
    for key_let in [79, 80, 81]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)
    
    # Enter
    curxy = self.PositionKey(self.key, curxy, XY(1, 2.06), 96)

    curxy.setx(numpadxy)
    curxy.transy(key_h)
    # 0, del
    curxy = self.PositionKey(self.key, curxy, XY(2.05, 1), 82)
    curxy = self.PositionKey(self.key, curxy, no_resize, 83)

  def CenterPad(self, homepadxy):
    if not self.center_keys:
      return
    no_resize = XY(1, 1) 
    key_w, key_h = self.key.key_w, self.key.key_h
    curxy = XY()
    curxy.set(homepadxy)
    for key_let in [99, 70, 119]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(homepadxy)
    curxy.transy(key_h * 1.2)
    # Ins to PgUp
    for key_let in [110, 102, 104]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(homepadxy)
    curxy.transy(key_h)
    # Del to PgDn
    for key_let in [111, 107, 109]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(homepadxy)
    curxy.transy(key_h * 2)
    curxy.transx(key_w)

    # Up arrow
    for key_let in [103]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)

    curxy.setx(homepadxy)
    curxy.transy(key_h)
    # Left, Down, Right
    for key_let in [105, 108, 106]:
      curxy = self.PositionKey(self.key, curxy, no_resize, key_let)



  def PositionKey(self, element, xy, dwh, scancode):
    """Position, stretch and change the letter after duplicating.
    Args:
      element: the element to duplicate
      xy: Position to move to.
      dwh: How much to make wider or higher 1 means don't change.
      scancode: New scancode to use in tspan
    """
    cur_key = copy.deepcopy(element.key)
    tspan = cur_key.find('.//' + addNS('tspan', 'svg'))
    tspan.text = self.scancodes.GetChr(scancode)
    # Set text position to center of document.
    cur_key.set('transform', 'translate(%d,%d)' % (xy.x, xy.y))
    rect = cur_key.find(addNS('rect', 'svg'))
    old_x = inkex.unittouu(rect.get('x'))
    old_y = inkex.unittouu(rect.get('y'))
    old_w = inkex.unittouu(rect.get('width'))
    old_h = inkex.unittouu(rect.get('height'))
    w = old_w * dwh.x
    h = old_h * dwh.y
    dx = w - old_w
    dy = h - old_h

    rect.set('width', str(w))
    rect.set('height', str(h))
    self.keys.append((scancode, xy.x, xy.y, w, h))
    if dwh.x == 1 and dwh.y == 1:
      # No resizing required.
      self.layer.append(cur_key)
      return xy.transx(element.key_w)
    for path in cur_key.iterchildren(addNS('text', 'svg')):
      TranslateXY(path, (dx / 2.0, 0))
      for tspan in path.iterchildren(addNS('tspan', 'svg')):
        TranslateXY(tspan, (dx / 2.0, 0))
    for path in cur_key.iterchildren(addNS('path', 'svg')):
      d = svg_regex.svg_parser.parse(path.get('d'))
      id = path.get('id')
      d2 = TranslatePath(d, (dx, dy), (10, 20))
      path.set('d', d2)
    self.layer.append(cur_key)
    return xy.transx(element.key_w + dx + 0.1 * dwh.x)

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
