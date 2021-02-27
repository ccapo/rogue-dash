from map.tile import Tile

class Map:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.tiles = self.initialize_tiles()

  def initialize_tiles(self):
    tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]

    tiles = self.column_room(tiles)

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

    return tiles

  def column_room(self, tiles):
    cx = int(self.width / 2)
    cy = int(self.height / 2)

    ax1 = cx - 10
    ax2 = ax1 + 1
    ay1 = cy
    ay2 = ay1 + 1

    for i in range(4):
      tiles[ax1][ay1].blocked = True
      tiles[ax1][ay1].block_sight = True
      tiles[ax2][ay1].blocked = True
      tiles[ax2][ay1].block_sight = True

      tiles[ax1][ay2].blocked = True
      tiles[ax1][ay2].block_sight = True
      tiles[ax2][ay2].blocked = True
      tiles[ax2][ay2].block_sight = True

      ay1 = ay1 - 6
      ay2 = ay1 + 1

    ax1 = cx - 10
    ax2 = ax1 + 1
    ay1 = cy + 6
    ay2 = ay1 + 1

    for i in range(3):
      tiles[ax1][ay1].blocked = True
      tiles[ax1][ay1].block_sight = True
      tiles[ax2][ay1].blocked = True
      tiles[ax2][ay1].block_sight = True

      tiles[ax1][ay2].blocked = True
      tiles[ax1][ay2].block_sight = True
      tiles[ax2][ay2].blocked = True
      tiles[ax2][ay2].block_sight = True

      ay1 = ay1 + 6
      ay2 = ay1 + 1

    ax1 = cx + 4
    ax2 = ax1 + 1
    ay1 = cy
    ay2 = ay1 + 1

    for i in range(4):
      tiles[ax1][ay1].blocked = True
      tiles[ax1][ay1].block_sight = True
      tiles[ax2][ay1].blocked = True
      tiles[ax2][ay1].block_sight = True

      tiles[ax1][ay2].blocked = True
      tiles[ax1][ay2].block_sight = True
      tiles[ax2][ay2].blocked = True
      tiles[ax2][ay2].block_sight = True

      ay1 = ay1 - 6
      ay2 = ay1 + 1

    ax1 = cx + 4
    ax2 = ax1 + 1
    ay1 = cy + 6
    ay2 = ay1 + 1

    for i in range(3):
      tiles[ax1][ay1].blocked = True
      tiles[ax1][ay1].block_sight = True
      tiles[ax2][ay1].blocked = True
      tiles[ax2][ay1].block_sight = True

      tiles[ax1][ay2].blocked = True
      tiles[ax1][ay2].block_sight = True
      tiles[ax2][ay2].blocked = True
      tiles[ax2][ay2].block_sight = True

      ay1 = ay1 + 6
      ay2 = ay1 + 1

    return tiles

  def is_blocked(self, x, y):
    if self.tiles[x][y].blocked:
      return True

    return False