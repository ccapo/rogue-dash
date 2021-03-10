class Tile:
  """
  A tile on a map. It may or may not be blocked, and may or may not block sight.
  """
  def __init__(self, blocked, block_sight = None):
    self.blocked = blocked
    self.previous_scent = 0.0
    self.current_scent = 0.0
    self.speed_modifier = 1.0
    
    # By default, if a tile is blocked, it also blocks sight
    if block_sight is None:
      block_sight = blocked
    
    self.block_sight = block_sight