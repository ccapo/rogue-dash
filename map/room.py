from map.tile import Tile

def column_room(w, h, tiles):
  cx = int(w / 2)
  cy = int(h / 2)

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