from random import uniform
import tcod as libtcod
from constants import StatusType, CharType

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
      return StatusType.OK

  # Move the entity by a given amount
  def move(self, dx, dy):
    self.x += dx
    self.y += dy

  def attack(self, target, engine):
    if target.is_dead() == False:
      damage = int(self.stats.ap * uniform(1.0, 1.125) - target.stats.dp)
      if damage > 0:
        engine.log.add("{} attacks {} for {} damage".format(self.name, target.name, damage), libtcod.light_grey)
      else:
        engine.log.add("{} attacks {} in vain!".format(self.name, target.name), libtcod.light_grey)
      target.stats.hp -= damage
      if target.stats.hp < 0:
        target.stats.hp = 0
      if target.is_dead() == True:
        engine.log.add("{} slays {} ".format(self.name, target.name), libtcod.light_grey)
        target.die()
        return True
    return False

  def is_dead(self):
    if self.stats is not None:
      return self.stats.hp <= 0
    return False

  def die(self):
    self.colour = libtcod.white
    if self.name == 'Player':
      self.colour = libtcod.light_red
    self.name = 'corpse'
    self.sym = CharType.SKULL
    self.blocks = False
    self.ai = None

  def render(self, con, camera_yoffset):
    libtcod.console_set_default_foreground(con, self.colour)
    libtcod.console_put_char(con, self.x, self.y - camera_yoffset, self.sym, libtcod.BKGND_NONE)

  def clear(self, con, camera_yoffset):
    libtcod.console_put_char(con, self.x, self.y - camera_yoffset, ' ', libtcod.BKGND_NONE)