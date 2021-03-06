from map.tile import Tile

class Room:
  def __init__(self, id, w, h, tiles, available_tiles):
    self.id = id
    self.w = w
    self.h = h
    self.tiles = tiles
    self.available_tiles = available_tiles

  def columns_template(self, p = None):
    cx = int(self.w / 2)
    cy = int(self.h / 2)

    ax1 = cx - 10
    ax2 = ax1 + 1
    ay1 = cy
    ay2 = ay1 + 1

    for i in range(4):
      self.tiles[ax1][ay1].set_blocked(True)
      self.tiles[ax2][ay1].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay1)
      self.available_tiles.remove(ax2 + self.w*ay1)

      self.tiles[ax1][ay2].set_blocked(True)
      self.tiles[ax2][ay2].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay2)
      self.available_tiles.remove(ax2 + self.w*ay2)

      ay1 = ay1 - 6
      ay2 = ay1 + 1

    ax1 = cx - 10
    ax2 = ax1 + 1
    ay1 = cy + 6
    ay2 = ay1 + 1

    for i in range(3):
      self.tiles[ax1][ay1].set_blocked(True)
      self.tiles[ax2][ay1].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay1)
      self.available_tiles.remove(ax2 + self.w*ay1)

      self.tiles[ax1][ay2].set_blocked(True)
      self.tiles[ax2][ay2].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay2)
      self.available_tiles.remove(ax2 + self.w*ay2)

      ay1 = ay1 + 6
      ay2 = ay1 + 1

    ax1 = cx + 4
    ax2 = ax1 + 1
    ay1 = cy
    ay2 = ay1 + 1

    for i in range(4):
      self.tiles[ax1][ay1].set_blocked(True)
      self.tiles[ax2][ay1].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay1)
      self.available_tiles.remove(ax2 + self.w*ay1)

      self.tiles[ax1][ay2].set_blocked(True)
      self.tiles[ax2][ay2].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay2)
      self.available_tiles.remove(ax2 + self.w*ay2)

      ay1 = ay1 - 6
      ay2 = ay1 + 1

    ax1 = cx + 4
    ax2 = ax1 + 1
    ay1 = cy + 6
    ay2 = ay1 + 1

    for i in range(3):
      self.tiles[ax1][ay1].set_blocked(True)
      self.tiles[ax2][ay1].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay1)
      self.available_tiles.remove(ax2 + self.w*ay1)

      self.tiles[ax1][ay2].set_blocked(True)
      self.tiles[ax2][ay2].set_blocked(True)
      self.available_tiles.remove(ax1 + self.w*ay2)
      self.available_tiles.remove(ax2 + self.w*ay2)

      ay1 = ay1 + 6
      ay2 = ay1 + 1

    return self.tiles, self.available_tiles