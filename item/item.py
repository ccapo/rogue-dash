import tcod as libtcod

class Item:
  # A generic object to represent an item or equipment
  def __init__(self, x, y, sym, colour, name, blocks = False, attr = None):
    self.x = x
    self.y = y
    self.sym = sym
    self.colour = colour
    self.name = name
    self.blocks = blocks

    # Attributes
    self.attr = attr

  def use(self):
    if self.attr is not None:
      print("Using {} ({})".format(self.name, self.attr.type.name))

  def render(self, con, camera_yoffset):
    libtcod.console_set_default_foreground(con, self.colour)
    libtcod.console_put_char(con, self.x, self.y - camera_yoffset, self.sym, libtcod.BKGND_NONE)

  def clear(self, con, camera_yoffset):
    libtcod.console_put_char(con, self.x, self.y - camera_yoffset, ' ', libtcod.BKGND_NONE)