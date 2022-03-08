class Tile:
  """
  A tile on a map.
  It may or may not be blocked.
  It has the player's past and present scent value.
  It also has a speed modifier
  """
  def __init__(self, blocked = True, speed_modifier = 1.0):
    self.blocked = blocked
    self.previous_scent = 0.0
    self.current_scent = 0.0
    self.speed_modifier = speed_modifier