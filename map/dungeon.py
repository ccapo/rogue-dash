import tcod as libtcod
import math
import os
from map.tile import Tile

class Dungeon():
  def __init__(self, width, height, camera_height, depth = 15, min_room_size = 4):
    self.width = width
    self.height = height
    self.camera_width = width
    self.camera_height = camera_height
    self.camera_yoffset = 0
    self.progress_yoffset = self.height - self.camera_height//2 - 1
    self.depth = depth
    self.min_room_size = min_room_size

    # a room fills a random part of the node or the maximum available space ?
    self.random_room = True
    # if true, there is always a wall on north & west side of a room
    self.room_walls = True

    # create the bsp
    self.bsp = libtcod.bsp_new_with_size(0, 0, self.width, self.height)

    # Tiles and list of available tiles
    self.available_tiles = []
    self.tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

    # build a new random bsp tree
    libtcod.bsp_remove_sons(self.bsp)
    if self.room_walls:
      libtcod.bsp_split_recursive(self.bsp, 0, self.depth,
                                  self.min_room_size + 1,
                                  self.min_room_size + 1, 1.5, 1.5)
    else:
      libtcod.bsp_split_recursive(self.bsp, 0, self.depth,
                                  self.min_room_size,
                                  self.min_room_size, 1.5, 1.5)

    # create the dungeon from the bsp
    libtcod.bsp_traverse_inverted_level_order(self.bsp, self.traverse_node)

    # sort list of available tiles
    self.available_tiles = sorted(self.available_tiles)

  # draw a vertical line
  def vline(self, x, y1, y2):
    if y1 > y2:
      y1, y2 = y2, y1
    for y in range(y1, y2 + 1):
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)

  # draw a vertical line up until we reach an empty space
  def vline_up(self, x, y):
    while y >= 0 and self.tiles[x][y].blocked:
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)
      y -= 1

  # draw a vertical line down until we reach an empty space
  def vline_down(self, x, y):
    while y < self.height and self.tiles[x][y].blocked:
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)
      y += 1

  # draw a horizontal line
  def hline(self, x1, y, x2):
    if x1 > x2:
      x1, x2 = x2, x1
    for x in range(x1, x2 + 1):
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)

  # draw a horizontal line left until we reach an empty space
  def hline_left(self, x, y):
    while x >= 0 and self.tiles[x][y].blocked:
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)
      x -= 1

  # draw a horizontal line right until we reach an empty space
  def hline_right(self, x, y):
    while x < self.width and self.tiles[x][y].blocked:
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)
      x += 1

  # the class building the dungeon from the bsp nodes
  def traverse_node(self, node, *dat):
    if libtcod.bsp_is_leaf(node):
      # calculate the room size
      minx = node.x + 1
      maxx = node.x + node.w - 1
      miny = node.y + 1
      maxy = node.y + node.h - 1
      if not self.room_walls:
        if minx > 1:
          minx -= 1
        if miny > 1:
          miny -=1
      if maxx == self.width - 1:
        maxx -= 1
      if maxy == self.height - 1:
        maxy -= 1
      if self.random_room:
        minx = libtcod.random_get_int(None, minx, maxx - self.min_room_size + 1)
        miny = libtcod.random_get_int(None, miny, maxy - self.min_room_size + 1)
        maxx = libtcod.random_get_int(None, minx + self.min_room_size - 1, maxx)
        maxy = libtcod.random_get_int(None, miny + self.min_room_size - 1, maxy)
      # resize the node to fit the room
      node.x = minx
      node.y = miny
      node.w = maxx-minx + 1
      node.h = maxy-miny + 1
      # dig the room
      for x in range(minx, maxx + 1):
        for y in range(miny, maxy + 1):
          self.tiles[x][y].blocked = False
          self.tiles[x][y].block_sight = False
          self.available_tiles.append(x + self.width*y)
    else:
      # resize the node to fit its sons
      left = libtcod.bsp_left(node)
      right = libtcod.bsp_right(node)
      node.x = min(left.x, right.x)
      node.y = min(left.y, right.y)
      node.w = max(left.x + left.w, right.x + right.w) - node.x
      node.h = max(left.y + left.h, right.y + right.h) - node.y
      # create a corridor between the two lower nodes
      if node.horizontal:
        # vertical corridor
        if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
          # no overlapping zone. we need a Z shaped corridor
          x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
          x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
          y = libtcod.random_get_int(None, left.y + left.h, right.y)
          self.vline_up(x1, y - 1)
          self.hline(x1, y, x2)
          self.vline_down(x2, y + 1)
        else:
          # straight vertical corridor
          minx = max(left.x, right.x)
          maxx = min(left.x + left.w - 1, right.x + right.w - 1)
          x = libtcod.random_get_int(None, minx, maxx)
          self.vline_down(x, right.y)
          self.vline_up(x, right.y - 1)
      else:
        # horizontal corridor
        if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
          # no overlapping zone. we need a Z shaped corridor
          y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
          y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
          x = libtcod.random_get_int(None, left.x + left.w, right.x)
          self.hline_left(x - 1, y1)
          self.vline(x, y1, y2)
          self.hline_right(x + 1, y2)
        else:
          # straight horizontal corridor
          miny = max(left.y, right.y)
          maxy = min(left.y + left.h - 1, right.y + right.h - 1)
          y = libtcod.random_get_int(None, miny, maxy)
          self.hline_left(right.x - 1, y)
          self.hline_right(right.x, y)
    return True

  def is_blocked(self, x, y):
    return self.tiles[x][y].blocked

  def move_camera(self, y):
    # New camera coordinates (top-left corner of the screen relative to the map)
    # Coordinates so that the target is at the center of the screen
    cy = y - self.camera_height//2;

    # Make sure the camera doesn't see outside the map
    if cy < 0:
      cy = 0
    if cy > self.height - self.camera_height - 1:
      cy = self.height - self.camera_height - 1

    self.camera_yoffset = cy

  def generate(self, player):
    desired_offset = (self.width - self.min_room_size)//2 + self.width*(self.height - self.min_room_size//2 - 1)
    threshold_min = 1000000
    key = None
    for offset in reversed(self.available_tiles):
      if abs(offset - desired_offset) < threshold_min:
        threshold_min = abs(offset - desired_offset)
        key = offset
    if key == None:
      print("Unable to find a matching offset")
      os.exit(1)
    px = key % self.width
    py = key//self.width
    player.x = px
    player.y = py

  # def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
  #   # Get a random number of monsters
  #   number_of_monsters = randint(0, max_monsters_per_room)

  #   # Get a random number of items
  #   number_of_items = randint(0, max_items_per_room)

  #   for i in range(number_of_monsters):
  #     # Choose a random location in the room
  #     x = randint(room.x1 + 1, room.x2 - 1)
  #     y = randint(room.y1 + 1, room.y2 - 1)

  #     if not any([entity for entity in entities if entity.x == x and entity.y == y]):
  #       if randint(0, 100) < 80:
  #         fighter_component = Fighter(hp=10, defense=0, power=3)
  #         ai_component = BasicMonster()

  #         monster = Entity(x, y, 'o', libtcod.desaturated_green, 'Orc', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
  #       else:
  #         fighter_component = Fighter(hp=16, defense=1, power=4)
  #         ai_component = BasicMonster()

  #         monster = Entity(x, y, 'T', libtcod.darker_green, 'Troll', blocks=True, fighter=fighter_component, render_order=RenderOrder.ACTOR, ai=ai_component)

  #       entities.append(monster)

  #   for i in range(number_of_items):
  #     x = randint(room.x1 + 1, room.x2 - 1)
  #     y = randint(room.y1 + 1, room.y2 - 1)

  #     if not any([entity for entity in entities if entity.x == x and entity.y == y]):
  #       item_component = Item(use_function=heal, amount=4)
  #       item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM, item=item_component)

  #       entities.append(item)