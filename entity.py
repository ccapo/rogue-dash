class Entity:
  """
  A generic object to represent players, enemies, items, etc.
  """
  def __init__(self, x, y, sym, colour, hp = 10, hpmax = 10, ap = 2, dp = 1, spd = 1):
    self.x = x
    self.y = y
    self.sym = sym
    self.colour = colour
    self.hp = hp
    self.hpmax = hpmax
    self.ap = ap
    self.dp = dp
    self.spd = spd

  def move(self, dx, dy):
    # Move the entity by a given amount
    self.x += dx
    self.y += dy