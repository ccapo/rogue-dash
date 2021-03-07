import tcod as libtcod
from random import randint
from map.tile import Tile
from map.rectangle import Rectangle

class Map:
  def __init__(self, width, height, camera_width, camera_height):
    self.width = width
    self.height = height
    self.camera_width = camera_width
    self.camera_height = camera_height
    self.camera_yoffset = 0
    self.progress_yoffset = self.height - self.camera_height//2 - 1
    self.available_tiles = []
    self.tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

  def generate(self, max_rooms, room_min_size, room_max_size, max_creatures_per_room, max_items_per_room, player, entities):
    rooms = []
    num_rooms = 0

    for r in range(max_rooms):
      # random width and height
      w = randint(room_min_size, room_max_size)
      h = randint(room_min_size, room_max_size)

      if num_rooms == 0:
        # First room is at the lowest point in the map
        x = (self.width - w)//2
        y = self.height - h - 1
      else:
        # random position without going out of the boundaries of the map
        x = randint(0, self.width - w - 1)
        y = randint(0, self.height - h - 1)

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
        else:
          # all rooms after the first:
          # connect it to the previous room with a tunnel

          # center coordinates of previous room
          (prev_x, prev_y) = rooms[num_rooms - 1].center()

          # flip a coin (random number that is either 0 or 1)
          if randint(0, 1) == 1:
            # first move horizontally, then vertically
            self.create_h_tunnel(prev_x, new_x, prev_y)
            self.create_v_tunnel(prev_y, new_y, new_x)
          else:
            # first move vertically, then horizontally
            self.create_v_tunnel(prev_y, new_y, prev_x)
            self.create_h_tunnel(prev_x, new_x, new_y)

          # Add creatures to room
          #self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)

        # finally, append the new room to the list
        rooms.append(new_room)
        num_rooms += 1

  def create_room(self, room):
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
      for y in range(room.y1 + 1, room.y2):
        self.tiles[x][y].blocked = False
        self.tiles[x][y].block_sight = False
        self.available_tiles.append(x + self.width*y)

  def create_h_tunnel(self, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)

  def create_v_tunnel(self, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
      self.tiles[x][y].blocked = False
      self.tiles[x][y].block_sight = False
      self.available_tiles.append(x + self.width*y)

  def is_blocked(self, x, y):
    if self.tiles[x][y].blocked:
      return True
    return False

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