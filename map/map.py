from map.tile import Tile
from map.room import column_room

class Map:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.available_tiles = []
    self.tiles = self.initialize_tiles()

  def initialize_tiles(self):
    tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]

    for x in range(self.width):
      tiles[x][0].blocked = True
      tiles[x][0].block_sight = True
      tiles[x][self.height - 1].blocked = True
      tiles[x][self.height - 1].block_sight = True

    for y in range(self.height):
      tiles[0][y].blocked = True
      tiles[0][y].block_sight = True
      tiles[self.width - 1][y].blocked = True
      tiles[self.width - 1][y].block_sight = True

    #tiles = column_room(self.width, self.height, tiles)

    return tiles

  def is_blocked(self, x, y):
    if self.tiles[x][y].blocked:
      return True

    return False