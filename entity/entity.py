import tcod as libtcod

class Entity:
  # A generic object to represent the player or creatures
  def __init__(self, x, y, sym, colour, name, blocks = True, stats = None, ai = None):
    self.x = x
    self.y = y
    self.sym = sym
    self.colour = colour
    self.name = name
    self.blocks = blocks

    # Stats
    self.stats = stats

    # AI
    self.ai = ai

  # Update entity AI
  def update(self, engine):
    if self.ai is not None:
      return self.ai.update(self, engine)
    else:
      return True

  # Move the entity by a given amount
  def move(self, dx, dy):
    self.x += dx
    self.y += dy

  def attack(self, target):
    print('You kick the ' + target.name + ' in the shins, much to its annoyance!')

  def render(self, con, camera_yoffset):
    libtcod.console_set_default_foreground(con, self.colour)
    libtcod.console_put_char(con, self.x, self.y - camera_yoffset, self.sym, libtcod.BKGND_NONE)

  def clear(self, con, camera_yoffset):
    libtcod.console_put_char(con, self.x, self.y - camera_yoffset, ' ', libtcod.BKGND_NONE)