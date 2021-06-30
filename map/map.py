import tcod as libtcod
import random
from map.ca import CellularAutomata
from entity.ai import AI
from entity.entity import Entity
from entity.stats import Stats
from item.item import Item
from item.attribute import Attribute
from constants import CharType, ItemType

class Map:
  def __init__(self, width, height, panel_height, stage):
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

    self.tiles = []

    # Define map generation parameters
    self.fail_limit = 50
    self.spawn_avoidance = 5
    self.max_creatures_per_cave = 3
    self.max_items_per_cave = 2
    self.max_equip_per_cave = 1

    # Create 16 unique creature symbols
    self.creature_symbols = []
    num_create_types = 16
    while num_create_types > 0:
      rsym = random.randint(CharType.SPRITE_441, CharType.SPRITE_1464)
      if rsym not in self.creature_symbols:
        self.creature_symbols.append(rsym)
        num_create_types -= 1

    # Define common colours
    self.colours = {
      'wall': libtcod.Color(0, 0, 100),
      'ground': libtcod.Color(50, 50, 150),
      'hole': libtcod.black
    }

    self.ca = CellularAutomata(self.map_width, self.map_height)

  def generate(self, entities, items, equips, exit):
    player = entities[0]

    # Generate tiles using Cellular Automata method
    self.tiles = self.ca.generateLevel()

    # Select player location and exit location
    exit_y = 1.0e10
    exit_x = None
    player_y = -1.0e10
    player_x = None
    for c in self.ca.caves:
      for o in c:
        x = o % self.map_width
        y = o // self.map_width
        if y < exit_y:
          exit_y = y
          exit_x = x
        if y > player_y:
          player_y = y
          player_x = x
    exit.x = exit_x
    exit.y = exit_y
    player.x = player_x
    player.y = player_y

    for c in self.ca.caves:
      # Add creatures to cave
      self.place_entities(c, player, entities)

      # Add items to cave
      self.place_items(c, player, items)

      # Add equipment to cave
      self.place_equipment(c, player, equips)

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

  # Place creatures in cave
  def place_entities(self, cave, player, entities):
    # Get a random number of monsters
    number_of_monsters = random.randint(1, self.max_creatures_per_cave)

    for i in range(number_of_monsters):
      # Choose a random location in the cave
      key = random.randint(0, len(cave) - 1)
      offset = cave[key]
      x = offset % self.map_width
      y = offset // self.map_width
      failcounter = 0
      diffbest = -1
      xbest = None
      ybest = None
      while((x - player.x)**2 + (y - player.y)**2 <= self.spawn_avoidance**2 and failcounter < self.fail_limit):
        key = random.randint(0, len(cave) - 1)
        offset = cave[key]
        x = offset % self.map_width
        y = offset // self.map_width
        diff = abs((x - player.x)**2 + (y - player.y)**2 - self.spawn_avoidance**2)
        if diff > diffbest:
          diffbest = diff
          xbest = x
          ybest = y
        failcounter += 1

      # Abort attempt if too many failures encountered
      if failcounter >= self.fail_limit:
        x = xbest
        y = ybest
        offset = x + self.map_width*y

      cave.remove(offset)

      if not any([entity for entity in entities if entity.x == x and entity.y == y]):
        r = random.randint(0, 100)
        # if r < 1:
        #   rsym = self.creature_symbols[0]
        #   stats = Stats(hp = 30, ap = 8, dp = 5, spd = 6)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_0', stats = stats, ai = AI('creature'))
        # elif r < 3:
        #   rsym = self.creature_symbols[1]
        #   stats = Stats(hp = 24, ap = 6, dp = 4, spd = 4)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_1', stats = stats, ai = AI('creature'))
        # elif r < 4:
        #   rsym = self.creature_symbols[2]
        #   stats = Stats(hp = 20, ap = 5, dp = 3, spd = 3)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_2', stats = stats, ai = AI('creature'))
        # elif r < 6:
        #   rsym = self.creature_symbols[3]
        #   stats = Stats(hp = 19, ap = 4, dp = 4, spd = 5)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_3', stats = stats, ai = AI('creature'))
        # elif r < 9:
        #   rsym = self.creature_symbols[4]
        #   stats = Stats(hp = 18, ap = 4, dp = 4, spd = 5)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_4', stats = stats, ai = AI('creature'))
        # elif r < 12:
        #   rsym = self.creature_symbols[5]
        #   stats = Stats(hp = 18, ap = 4, dp = 4, spd = 4)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_5', stats = stats, ai = AI('creature'))
        # elif r < 15:
        #   rsym = self.creature_symbols[6]
        #   stats = Stats(hp = 16, ap = 4, dp = 3, spd = 4)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_6', stats = stats, ai = AI('creature'))
        # elif r < 19:
        #   rsym = self.creature_symbols[7]
        #   stats = Stats(hp = 15, ap = 4, dp = 3, spd = 4)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_7', stats = stats, ai = AI('creature'))
        # elif r < 24:
        #   rsym = self.creature_symbols[8]
        #   stats = Stats(hp = 15, ap = 3, dp = 2, spd = 3)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_8', stats = stats, ai = AI('creature'))
        # elif r < 30:
        #   rsym = self.creature_symbols[9]
        #   stats = Stats(hp = 15, ap = 3, dp = 2, spd = 2)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_9', stats = stats, ai = AI('creature'))
        # elif r < 37:
        #   rsym = self.creature_symbols[10]
        #   stats = Stats(hp = 13, ap = 3, dp = 2, spd = 3)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_10', stats = stats, ai = AI('creature'))
        # elif r < 45:
        #   rsym = self.creature_symbols[11]
        #   stats = Stats(hp = 12, ap = 3, dp = 2, spd = 2)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_11', stats = stats, ai = AI('creature'))
        # elif r < 55:
        #   rsym = self.creature_symbols[12]
        #   stats = Stats(hp = 11, ap = 2, dp = 2, spd = 3)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_12', stats = stats, ai = AI('creature'))
        # elif r < 67:
        #   rsym = self.creature_symbols[13]
        #   stats = Stats(hp = 11, ap = 2, dp = 2, spd = 2)
        #   creature = Entity(x, y, rsym, libtcod.white, 'Creature_13', stats = stats, ai = AI('creature'))
        if r < 50:
          rsym = self.creature_symbols[14]
          stats = Stats(hp = 10, ap = 2, dp = 1, spd = 2)
          creature = Entity(x, y, rsym, libtcod.white, 'Creature_14', stats = stats, ai = AI('creature'))
        else:
          rsym = self.creature_symbols[15]
          stats = Stats(hp = 10, ap = 1, dp = 1, spd = 2)
          creature = Entity(x, y, rsym, libtcod.white, 'Creature_15', stats = stats, ai = AI('creature'))

        entities.append(creature)

  # Place items in cave
  def place_items(self, cave, player, items):
    # Get a random number of items
    number_of_items = random.randint(0, self.max_items_per_cave)

    for i in range(number_of_items):
      key = random.randint(0, len(cave) - 1)
      offset = cave[key]
      x = offset % self.map_width
      y = offset // self.map_width
      failcounter = 0
      diffbest = -1
      xbest = None
      ybest = None
      while((x - player.x)**2 + (y - player.y)**2 <= self.spawn_avoidance**2) and failcounter < self.fail_limit:
        key = random.randint(0, len(cave) - 1)
        offset = cave[key]
        x = offset % self.map_width
        y = offset // self.map_width
        diff = abs((x - player.x)**2 + (y - player.y)**2 - self.spawn_avoidance**2)
        if diff > diffbest:
          diffbest = diff
          xbest = x
          ybest = y
        failcounter += 1

      # Abort attempt if too many failures encountered
      if failcounter >= self.fail_limit:
        x = xbest
        y = ybest
        offset = x + self.map_width*y

      cave.remove(offset)

      if not any([item for item in items if item.x == x and item.y == y]):
        r = random.randint(0, 100)
        if r < 10:
          attr = Attribute(type = ItemType.POTION_ATK, value = 2, duration = 30.0)
          item = Item(x, y, CharType.POTION_GREEN, libtcod.white, 'Attack Potion', attr = attr)
        elif r < 20:
          attr = Attribute(type = ItemType.POTION_DEF, value = 2, duration = 30.0)
          item = Item(x, y, CharType.POTION_BLUE, libtcod.white, 'Defense Potion', attr = attr)
        elif r < 30:
          attr = Attribute(type = ItemType.POTION_SPD, value = 2, duration = 30.0)
          item = Item(x, y, CharType.POTION_YELLOW, libtcod.white, 'Speed Potion', attr = attr)
        else:
          attr = Attribute(type = ItemType.POTION_HEAL, value = 4)
          item = Item(x, y, CharType.POTION_RED, libtcod.white, 'Healing Potion', attr = attr)

        items.append(item)

  # Place equipment in cave
  def place_equipment(self, cave, player, equips):
    # Get a random number of items
    number_of_equip = random.randint(0, self.max_equip_per_cave)

    for i in range(number_of_equip):
      key = random.randint(0, len(cave) - 1)
      offset = cave[key]
      x = offset % self.map_width
      y = offset // self.map_width
      failcounter = 0
      diffbest = -1
      xbest = None
      ybest = None
      while((x - player.x)**2 + (y - player.y)**2 <= self.spawn_avoidance**2) and failcounter < self.fail_limit:
        key = random.randint(0, len(cave) - 1)
        offset = cave[key]
        x = offset % self.map_width
        y = offset // self.map_width
        diff = abs((x - player.x)**2 + (y - player.y)**2 - self.spawn_avoidance**2)
        if diff > diffbest:
          diffbest = diff
          xbest = x
          ybest = y
        failcounter += 1

      # Abort attempt if too many failures encountered
      if failcounter >= self.fail_limit:
        x = xbest
        y = ybest
        offset = x + self.map_width*y

      cave.remove(offset)

      if not any([equip for equip in equips if equip.x == x and equip.y == y]):
        r = random.randint(0, 100)
        if r < 10:
          stats = Stats(hp = 0, ap = 2, dp = 0, spd = 0)
          equip = Entity(x, y, CharType.RING_RED, libtcod.white, 'Ring of Attack', stats = stats)
        elif r < 20:
          stats = Stats(hp = 0, ap = 0, dp = 2, spd = 0)
          equip = Entity(x, y, CharType.RING_GREEN, libtcod.white, 'Ring of Defense', stats = stats)
        elif r < 30:
          stats = Stats(hp = 0, ap = 0, dp = 0, spd = 2)
          equip = Entity(x, y, CharType.RING_BLUE, libtcod.white, 'Ring of Speed', stats = stats)
        elif r < 40:
          stats = Stats(hp = 0, ap = 0, dp = 1, spd = 0)
          equip = Entity(x, y, CharType.SHIELD_BROWN, libtcod.white, 'Wooden Shield', stats = stats)
        elif r < 50:
          stats = Stats(hp = 0, ap = 0, dp = 2, spd = 0)
          equip = Entity(x, y, CharType.SHIELD_GREY, libtcod.white, 'Bronze Shield', stats = stats)
        elif r < 60:
          stats = Stats(hp = 0, ap = 0, dp = 4, spd = 0)
          equip = Entity(x, y, CharType.SHIELD_GOLD, libtcod.white, 'Golden Shield', stats = stats)
        elif r < 70:
          stats = Stats(hp = 0, ap = 1, dp = 0, spd = 0)
          equip = Entity(x, y, CharType.SWORD_BASIC, libtcod.white, 'Bronze Sword', stats = stats)
        elif r < 80:
          stats = Stats(hp = 0, ap = 2, dp = 0, spd = 0)
          equip = Entity(x, y, CharType.SWORD_STEEL, libtcod.white, 'Steel Sword', stats = stats)
        else:
          stats = Stats(hp = 0, ap = 4, dp = 0, spd = 0)
          equip = Entity(x, y, CharType.SWORD_GOLD, libtcod.white, 'Golden Sword', stats = stats)

        equips.append(equip)

  # Update map
  def update(self, player, dt):
    # Update map progress offset
    self.update_map_progress(dt)

    self.move_camera()

    self.update_scent(player)

  def render(self, con):
    for y in range(self.camera_yoffset, self.camera_height + self.camera_yoffset + 1):
      for x in range(self.camera_width):
        wall = self.tiles[x][y].blocked
        if wall:
          libtcod.console_set_char_background(con, x, y - self.camera_yoffset, self.colours.get('wall'), libtcod.BKGND_SET)
        else:
          libtcod.console_set_char_background(con, x, y - self.camera_yoffset, self.colours.get('ground'), libtcod.BKGND_SET)