class Entity:
  """
  A generic object to represent the player, creatures, items and equipment
  """
  def __init__(self, x, y, sym, colour, name, blocks = True, stats = None, attr = None, ai = None):
    self.x = x
    self.y = y
    self.sym = sym
    self.colour = colour
    self.name = name
    self.blocks = blocks

    # Stats
    self.stats = stats

    # Attributes
    self.attr = attr

    # AI
    self.ai = ai

  # Move the entity by a given amount
  def move(self, dx, dy):
    self.x += dx
    self.y += dy

  def use(self):
    if self.attr is not None:
      print('Using ' + self.name + ' (' + self.attr.type + ')')

  def update(self):
    if self.ai is not None:
      print('AI for ' + self.name + ' is: ' + self.ai.update())