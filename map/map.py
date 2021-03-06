from map.tile import Tile
from map.room import Room

class Map:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.available_tiles = []
    self.tiles = []
    self.initialize()

  def initialize(self):
    self.tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]
    self.available_tiles = [i for i in range(self.width*self.height)]

    for x in range(self.width):
      self.tiles[x][0].set_blocked(True)
      self.tiles[x][self.height - 1].set_blocked(True)

    for y in range(self.height):
      self.tiles[0][y].set_blocked(True)
      self.tiles[self.width - 1][y].set_blocked(True)

  def create_room(self, id):
    room = Room(id, self.width, self.height, self.tiles, self.available_tiles)
    self.tiles, self.available_tiles = room.columns_template()

  def is_blocked(self, x, y):
    if self.tiles[x][y].blocked:
      return True

    return False