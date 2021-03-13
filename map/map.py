import tcod as libtcod
from random import randint
from map.tile import Tile
from map.rectangle import Rectangle
from entity.ai import AI
from entity.entity import Entity
from entity.stats import Stats
from item.item import Item
from item.attribute import Attribute
from constants import CharType, ItemType

class Map:
  def __init__(self, width, height, panel_height, stage = 1):
    # Define map width and height
    self.map_width = width
    self.map_height = 3*height

    # Define camera width, height and position
    self.camera_width = width
    self.camera_height = height - panel_height
    self.camera_yoffset = 0

    # Define stage
    self.stage = stage

    # Define map auto-scrolling rate
    self.elapsed = -1.0
    self.min_delay_threshold = 0.25
    self.max_delay_threshold = 4.0
    self.delta_delay_threshold = 0.25
    self.progress_yoffset = self.map_height - self.camera_height//2 - 1

    self.available_tiles = []
    self.tiles = [[Tile(True) for y in range(self.map_height)] for x in range(self.map_width)]

    # Define map generation parameters
    self.max_room_size = 8
    self.min_room_size = 4
    self.max_rooms = 80
    self.max_creatures_per_room = 3
    self.max_items_per_room = 2
    self.max_equip_per_room = 1

    # Define common colours
    self.colours = {
      'wall': libtcod.Color(0, 0, 100),
      'ground': libtcod.Color(50, 50, 150),
      'hole': libtcod.black
    }

  def generate(self, entities, items):
    player = entities[0]
    rooms = []
    num_rooms = 0

    for r in range(self.max_rooms):
      # random width and height
      w = randint(self.min_room_size, self.max_room_size)
      h = randint(self.min_room_size, self.max_room_size)

      if num_rooms == 0:
        # First room is at the lowest point in the map
        x = (self.map_width - w)//2
        y = self.map_height - h - 2
      else:
        # random position without going out of the boundaries of the map
        x = randint(0, self.map_width - w - 1)
        y = randint(0, self.map_height - h - 1)

      # Rectangle class makes rectangular rooms
      new_room = Rectangle(x, y, w, h)

      # run through the other rooms and see if they intersect with this one
      for other_room in rooms:
        if new_room.intersect(other_room):
          break
      else:
        # this means there are no intersections, so this room is valid

        # "paint" it to the map's tiles
        self.create_room(new_room)

        # center coordinates of new room, will be useful later
        (new_x, new_y) = new_room.center()

        if num_rooms == 0:
          # this is the first room, where the player starts
          player.x = new_x
          player.y = new_y

        # finally, append the new room to the list
        rooms.append(new_room)
        num_rooms += 1

    # Sort rooms and connect closest
    rooms_sorted = sorted(rooms)
    for i in range(num_rooms - 1):
      # connect it to the previous room with a tunnel
      r = rooms_sorted[i]
      s = rooms_sorted[i + 1]

      # center coordinates of next room
      (next_x, next_y) = s.center()

      # center coordinates of previous room
      (prev_x, prev_y) = r.center()

      if randint(0, 1) == 1:
        # first move horizontally, then vertically
        self.create_h_tunnel(prev_x, next_x, prev_y)
        self.create_v_tunnel(prev_y, next_y, next_x)
      else:
        # first move vertically, then horizontally
        self.create_v_tunnel(prev_y, next_y, prev_x)
        self.create_h_tunnel(prev_x, next_x, next_y)

    for i in range(1, num_rooms):
      r = rooms[i]

      # Add creatures to room
      self.place_entities(r, entities)

    for i in range(1, num_rooms):
      r = rooms[i]

      # Add items and equipment to room
      self.place_items(r, items)

  def create_room(self, room):
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
      for y in range(room.y1 + 1, room.y2):
        self.tiles[x][y].blocked = False
        self.tiles[x][y].block_sight = False
        self.available_tiles.append(x + self.map_width*y)

  def create_h_tunnel(self, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False

  def create_v_tunnel(self, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False

  def is_blocked(self, x, y):
    if self.tiles[x][y].blocked or y < self.camera_yoffset or y > self.camera_height + self.camera_yoffset - 1:
      return True
    return False

  # Update map progress
  def update_map_progress(self, dt):
    self.elapsed += dt
    if self.elapsed > self.delay_threshold():
      self.elapsed = 0.0
      self.progress_yoffset -= 1
      if self.progress_yoffset < 0:
        self.progress_yoffset = 0

  # Reset elapsed map progress counter, giving the user one second delay
  def reset_elapsed(self):
    self.elapsed = -1.0

  def delay_threshold(self):
    return max(self.min_delay_threshold, self.max_delay_threshold - (self.stage - 1) * self.delta_delay_threshold)

  def move_camera(self):
    # New camera coordinates (top-left corner of the screen relative to the map)
    # Coordinates so that the target is at the center of the screen
    cy = self.progress_yoffset - self.camera_height//2

    # Make sure the camera doesn't see outside the map
    if cy < 0:
      cy = 0
    if cy > self.map_height - self.camera_height - 1:
      cy = self.map_height - self.camera_height - 1

    self.camera_yoffset = cy

  # Update player's scent
  def update_scent(self, player):
    dx = (-1, 0, 1, -1, 1, -1, 0, 1)
    dy = (-1, -1, -1, 0, 0, 1, 1, 1)
    # Diffusion coefficient
    dcoef = 1.0/8.0
    lamb = 1.0

    # Set the scent for the current location of the player
    self.tiles[player.x][player.y].previous_scent = 0.75

    for x in range(1, self.map_width - 1):
      for y in range(1, self.map_height - 1):
        if not self.is_blocked(x, y):
          sdiff = 0.0
          for z in range(8):
            xp = x + dx[z]
            yp = y + dy[z]
            sdiff += self.tiles[xp][yp].previous_scent - self.tiles[x][y].previous_scent
          self.tiles[x][y].current_scent = lamb*(self.tiles[x][y].previous_scent + dcoef*sdiff)
        else:
          self.tiles[x][y].current_scent = 0.0

    for x in range(1, self.map_width - 1):
      for y in range(1, self.map_height - 1):
        self.tiles[x][y].previous_scent = self.tiles[x][y].current_scent

  # Place creatures in rooms
  def place_entities(self, room, entities):
    # Get a random number of monsters
    number_of_monsters = randint(0, self.max_creatures_per_room)

    for i in range(number_of_monsters):
      # Choose a random location in the room
      x = randint(room.x1 + 1, room.x2 - 1)
      y = randint(room.y1 + 1, room.y2 - 1)

      if not any([entity for entity in entities if entity.x == x and entity.y == y]):
        rsym = randint(441, 1464)
        if randint(0, 100) < 80:
          #fighter_component = Fighter(hp=10, defense=0, power=3)
          #ai_component = BasicMonster()
          stats = Stats(hp = 10, ap = 3, dp = 0)
          creature = Entity(x, y, rsym, libtcod.white, 'Orc', stats = stats, ai = AI('creature'))
        else:
          #fighter_component = Fighter(hp=16, defense=1, power=4)
          #ai_component = BasicMonster()
          stats = Stats(hp = 16, ap = 4, dp = 1)
          creature = Entity(x, y, rsym, libtcod.white, 'Troll', stats = stats, ai = AI('creature'))

        entities.append(creature)

  # Place items in rooms
  def place_items(self, room, items):
    # Get a random number of items
    number_of_items = randint(0, self.max_items_per_room)

    for i in range(number_of_items):
      x = randint(room.x1 + 1, room.x2 - 1)
      y = randint(room.y1 + 1, room.y2 - 1)

      if not any([item for item in items if item.x == x and item.y == y]):
        attr = Attribute(type = ItemType.POTION_HEAL, value = 4)
        item = Item(x, y, CharType.POTION_RED, libtcod.white, 'Healing Potion', attr = attr)

        items.append(item)

  # Update map
  def update(self, player, dt):
    # Update map progress offset
    self.update_map_progress(dt)

    self.move_camera()

    self.update_scent(player)

  def render(self, con):
    for y in range(self.camera_yoffset, self.camera_height + self.camera_yoffset + 1):
      for x in range(self.camera_width):
        wall = self.tiles[x][y].block_sight
        if wall:
          libtcod.console_set_char_background(con, x, y - self.camera_yoffset, self.colours.get('wall'), libtcod.BKGND_SET)
        else:
          libtcod.console_set_char_background(con, x, y - self.camera_yoffset, self.colours.get('ground'), libtcod.BKGND_SET)