import tcod as libtcod

import time
from random import randint
from constants import StatusType, CharType, ScorecardType
from client import Client
from entity.entity import Entity
from entity.stats import Stats
from entity.ai import AI
from map.map import Map
from log import Log
from menu import Menu
from handlers import handle_keys

LEVEL_START = 16

class Engine:
  def __init__(self, screen_width = 50, screen_height = 40):
    # Define flag to display menu
    self.state = 'menu'

    # Define screen width and height
    self.screen_width = screen_width
    self.screen_height = screen_height

    # Define height of panel
    self.panel_height = 9

    # Define stage number
    self.stage = LEVEL_START

    # Define message log and status panel
    self.bar_width = 15
    self.panel_yoffset = self.screen_height - self.panel_height + 1
    self.message_xoffset = self.bar_width + 2
    self.message_width = self.screen_width - self.bar_width - 2
    self.message_height = self.panel_height - 2

    # Default font path and number of rows and columns
    self.font_path = 'data/fonts/arial16x16-ext.png'
    self.font_ncols = 32
    self.font_nrows = 46

    # Load custom font
    self.load_custom_font()

    # HTTP client
    self.client = Client()

    # Initialize scorecard
    self.scorecard = [0 for i in range(ScorecardType.NRECORDS)]
    self.record = self.client.read_score()

    # Define player and other entities
    self.player = Entity(0, 0, CharType.PLAYER_RIGHT, libtcod.white, 'Player', stats = Stats(spd = 12), ai = AI('player'))
    self.entities = [self.player]

    # Define list of items
    self.items = []

    # Define list of equipment
    self.equips = []

    # Define exit for current stage
    self.exit = Entity(0, 0, CharType.STAIRS_DOWN, libtcod.white, 'Exit', blocks = False)

    # Create menu
    self.menu = Menu(self.screen_width, self.screen_height)

    # Create map
    self.next_stage = False
    self.map = Map(self.screen_width, self.screen_height, self.panel_height, self.stage)

    # Initialize the root console
    libtcod.console_init_root(self.screen_width, self.screen_height, 'rogue-dash (2021 7DRL)', False)

    self.log = Log(self.message_xoffset, self.message_width, self.message_height)
    self.log.add('Welcome to rogue-dash!', libtcod.green)

    # Create consoles
    self.con = libtcod.console_new(self.screen_width, self.screen_height)
    self.panel = libtcod.console_new(self.screen_width, self.panel_height)

    # Define input handlers
    self.key = libtcod.Key()
    self.mouse = libtcod.Mouse()

  # Upload score to game server
  def upload_score(self):
    if any([s > 0 for s in self.scorecard]):
      self.client.upload_score(self.scorecard)
      self.scorecard = [0 for i in range(ScorecardType.NRECORDS)]
      self.record = self.client.read_score()

  # Return blocking entity at location if it exists
  def get_entities(self, dx, dy):
    for entity in self.entities:
      if entity.blocks and entity.x == dx and entity.y == dy:
        return entity
    return None

  # Return items at location if it exists
  def get_items(self, dx, dy):
    for item in self.items:
      if item.x == dx and item.y == dy:
        return item
    return None

  # Return exit if it exists
  def get_exit(self, dx, dy):
    if self.exit.x == dx and self.exit.y == dy:
      return self.exit
    return None

  # Generate a new stage
  def generateStage(self, reset = False):
    self.next_stage = False
    self.progress_yoffset = 0
    if reset:
      self.stage = LEVEL_START
      self.player = Entity(0, 0, CharType.PLAYER_RIGHT, libtcod.white, 'Player', stats = Stats(spd = 12), ai = AI('player'))
    else:
      self.stage += 1
    self.entities = [self.player]
    self.items = []
    self.equips = []
    self.exit = Entity(0, 0, CharType.STAIRS_DOWN, libtcod.white, 'Exit', blocks = False)
    self.map = Map(self.screen_width, self.screen_height, self.panel_height, self.stage)
    self.map.generate(self.entities, self.items, self.equips, self.exit)
    if reset:
      self.log.clear()
      self.log.add('Welcome to rogue-dash!', libtcod.green)
    else:
      self.log.add("Welcome to stage {}!".format(self.stage), libtcod.green)

  # Update all entities and the map
  def update(self, dt):
    status = StatusType.OK
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, self.key, self.mouse)

    if self.key.vk == libtcod.KEY_DELETE:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    if self.state == 'menu':
      self.menu.update(self.record)

      if self.key.vk == libtcod.KEY_ENTER:
        self.state = 'game'
        self.generateStage(reset = True)
        status = StatusType.DIED
      elif self.key.vk == libtcod.KEY_ESCAPE:
        status = StatusType.QUIT
    else:
      # If the player uses the exit, advance to the next stage
      if self.next_stage:
        self.generateStage()

      # Update map
      self.map.update(self.player, dt)

      # Update all entities
      for entity in self.entities:
        update_status = entity.update(self)
        if update_status > 0:
          status = update_status

      if status == StatusType.DIED:
        self.render()
        self.state = 'menu'

    return status

  # Render all items and entities
  def render(self):
    libtcod.console_set_fade(255, libtcod.black)

    # Set background for panel to black, and clear
    libtcod.console_set_default_background(self.con, libtcod.black)
    libtcod.console_set_default_foreground(self.con, libtcod.white)
    libtcod.console_clear(self.con)

    # Set background for panel to black, and clear
    libtcod.console_set_default_background(self.panel, libtcod.black)
    libtcod.console_set_default_foreground(self.panel, libtcod.white)
    libtcod.console_clear(self.panel)

    if self.state == 'menu':
      self.menu.render(self.con)

      # Blit con to root console
      libtcod.console_blit(self.con, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

      # Flush buffer to the root console
      libtcod.console_flush()
    else:
      # Draw all the tiles visble from the camera
      self.map.render(self.con)

      # Draw exit
      self.exit.render(self.con, self.map.camera_yoffset)

      # Draw all items
      for item in self.items:
        item.render(self.con, self.map.camera_yoffset)

      # Draw all equipment
      for equip in self.equips:
        equip.render(self.con, self.map.camera_yoffset)

      # Draw all entities in reverse order
      for entity in reversed(self.entities):
        entity.render(self.con, self.map.camera_yoffset)

      # Blit con to root console
      libtcod.console_blit(self.con, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

      # Print the game messages, one line at a time
      y = 1
      for message in self.log.messages:
        libtcod.console_set_default_foreground(self.panel, message['colour'])
        libtcod.console_print_ex(self.panel, self.log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message['text'])
        y += 1

      # Render health bar and player stats
      self.render_stats(self.panel, 1, 1, self.player)

      # Blit panel to root console
      libtcod.console_blit(self.panel, 0, 0, self.screen_width, self.panel_height, 0, 0, self.panel_yoffset)

      # Flush buffer to the root console
      libtcod.console_flush()

      # Clear all entities
      for entity in self.entities:
        entity.clear(self.con, self.map.camera_yoffset)

      # Clear all equipment
      for equip in self.equips:
        equip.clear(self.con, self.map.camera_yoffset)

      # Clear all items
      for item in self.items:
        item.clear(self.con, self.map.camera_yoffset)

      # Clear exit
      self.exit.clear(self.con, self.map.camera_yoffset)

  # Render bar in panel
  def render_stats(self, panel, x, y, entity):
    hp_bar_width = int(float(entity.stats.hp) / entity.stats.hpmax * self.bar_width)

    libtcod.console_set_default_background(panel, libtcod.darker_red)
    libtcod.console_rect(panel, x, y, self.bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, libtcod.light_red)
    if hp_bar_width > 0:
      libtcod.console_rect(panel, x, y, hp_bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + self.bar_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, 'HP: {}/{}'.format(entity.stats.hp, entity.stats.hpmax))

    # Dash bar
    y += 1
    dash_elapsed = 0.0
    if entity.ai is not None:
      dash_elapsed = entity.ai.dash_elapsed
    dash_bar_width = int(float(entity.stats.spd*dash_elapsed) / 50.0 * self.bar_width)

    libtcod.console_set_default_background(panel, libtcod.darker_green)
    libtcod.console_rect(panel, x, y, self.bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, libtcod.light_green)
    if dash_bar_width > 0:
      libtcod.console_rect(panel, x, y, dash_bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + self.bar_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, 'Dash')

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_set_default_foreground(panel, libtcod.white)

    y += 1
    y += 1; libtcod.console_print_ex(panel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, 'ATK: {}'.format(entity.stats.ap))
    y += 1; libtcod.console_print_ex(panel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, 'DEF: {}'.format(entity.stats.dp))
    y += 1; libtcod.console_print_ex(panel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, 'SPD: {}'.format(entity.stats.spd))

  # Fade to black
  def fadeOut(self, nframes = 24, dt = 0.05):
    for i in range(nframes + 1):
      fade = 255*(nframes - i) // nframes
      libtcod.console_set_fade(fade, libtcod.black)
      libtcod.console_flush()
      time.sleep(dt)

  # Load custome fonts
  def load_custom_font(self):
    # Load font
    libtcod.console_set_custom_font(self.font_path, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, self.font_ncols, self.font_nrows)

    # Assign extra ascii keys
    x = -1
    y = 8
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.STAIRS_UP), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.STAIRS_DOWN), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.HOLE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.WATER_01), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.WATER_02), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.LAVA_01), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.LAVA_02), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHEST_OPEN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHEST_CLOSED), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.POTION_YELLOW), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.POTION_RED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.POTION_GREEN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.POTION_BLUE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.KEY), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RING_RED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RING_GREEN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RING_BLUE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RING_RED_BIG), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RING_GREEN_BIG), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RING_BLUE_BIG), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHIELD_BROWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHIELD_GREY), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHIELD_GOLD), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SWORD_BASIC), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SWORD_STEEL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SWORD_GOLD), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ARMOUR_BROWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ARMOUR_YELLOW), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ARMOUR_RED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ARMOUR_GREEN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ARMOUR_BLUE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ARMOUR_MITHRIL), x, y)
    x = -1
    y += 1

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHARGEBAR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PLAYER_RIGHT), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PLAYER_DOWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PLAYER_LEFT), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PLAYER_UP), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GUARDIAN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.KEEPER), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PERSON_MALE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PERSON_FEMALE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GUARD), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.WARLOCK_PURPLE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.NECROMANCER_APPENTICE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.NECROMANCER_MASTER), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DARKELF_ARCHER), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DARKELF_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DARKELF_MAGE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DWARF_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DWARF_AXEBEARER), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DWARF_MAGE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DWARF_HERO), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.UNDEAD_DWARF_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.UNDEAD_DWARF_AXEBEARER), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.UNDEAD_DWARF_MAGE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.UNDEAD_DWARF_HERO), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GOBLIN_PEON), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GOBLIN_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GOBLIN_MAGE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.IMP_BLUE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.IMP_RED), x, y)
    x = -1
    y += 1

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORGE_PEON_GREEN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORGE_WARRIOR_GREEN), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORGE_PEON_RED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORGE_WARRIOR_RED), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SKELETON_PEON), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SKELETON_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SKELETON_HERO), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SKELETON_MAGE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORC_PEON), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORC_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORC_HERO), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.ORC_MAGE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMON_PEON), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMON_HERO), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMON_MAGE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLAYER_WARRIOR), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLAYER_MAGE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SKULL), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GOLEM_GREY), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GOLEM_BROWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.GOLEM_RED), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SLIME_BROWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SLIME_GREEN), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.EYEBALL), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.VERMIN_BROWN), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SNAKE_GREEN), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.RUBBLE_PILE), x, y)
    x = -1
    y += 1

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SCORPIAN_YELLOW), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SCORPIAN_BLACK), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPIDER_BLACK), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPIDER_RED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPIDER_GREEN), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PYTHON_RED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PYTHON_BROWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.PYTHON_YELLOW), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BAT_BROWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BAT_BLUE), x, y)

    # Environment Tiles
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_A), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_B), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_C), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_D), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_E), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_F), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TREE_G), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHRUB_A), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHRUB_B), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHRUB_C), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SHRUB_D), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MUSHROOM), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLOWERS_WHITE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLOWERS_BLUE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TEMPLE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TOWN), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CAVE), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BED), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.TABLE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BOOKCASE), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAIR_RIGHT), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAIR_LEFT), x, y)
    x = -1
    y += 1

    # Minor Bosses (Upper Portion)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_WHITE_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_WHITE_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_RED_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_RED_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CYCLOPS_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CYCLOPS_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_RED_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_RED_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_YELLOW_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_YELLOW_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREEN_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREEN_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_BLUE_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_BLUE_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREY_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREY_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MINOTAUR_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MINOTAUR_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.LIZARD_GIANT_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.LIZARD_GIANT_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MEDUSA_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MEDUSA_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLYING_BRAIN_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLYING_BRAIN_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SLIMELORD_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SLIMELORD_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHOLDER_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHOLDER_UR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHEMOTH_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHEMOTH_UR), x, y)

    # Final Boss (Upper Portion)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FINAL_BOSS_UL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FINAL_BOSS_UR), x, y)
    x = -1
    y += 1

    # Minor Bosses (Lower Portion)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_WHITE_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_WHITE_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_RED_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DEMONLORD_RED_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CYCLOPS_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CYCLOPS_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_RED_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_RED_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_YELLOW_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_YELLOW_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREEN_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREEN_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_BLUE_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_BLUE_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREY_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.DRAGON_LARGE_GREY_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MINOTAUR_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MINOTAUR_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.LIZARD_GIANT_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.LIZARD_GIANT_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MEDUSA_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.MEDUSA_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLYING_BRAIN_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FLYING_BRAIN_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SLIMELORD_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SLIMELORD_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHOLDER_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHOLDER_LR), x, y)

    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHEMOTH_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.BEHEMOTH_LR), x, y)

    # Final Boss (Lower Portion)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FINAL_BOSS_LL), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.FINAL_BOSS_LR), x, y)

    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_441), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_442), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_443), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_444), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_445), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_446), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_447), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_448), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_449), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_450), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_451), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_452), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_453), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_454), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_455), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_456), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_457), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_458), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_459), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_460), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_461), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_462), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_463), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_464), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_465), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_466), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_467), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_468), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_469), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_470), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_471), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_472), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_473), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_474), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_475), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_476), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_477), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_478), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_479), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_480), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_481), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_482), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_483), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_484), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_485), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_486), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_487), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_488), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_489), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_490), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_491), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_492), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_493), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_494), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_495), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_496), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_497), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_498), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_499), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_500), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_501), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_502), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_503), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_504), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_505), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_506), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_507), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_508), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_509), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_510), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_511), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_512), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_513), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_514), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_515), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_516), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_517), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_518), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_519), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_520), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_521), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_522), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_523), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_524), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_525), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_526), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_527), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_528), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_529), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_530), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_531), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_532), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_533), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_534), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_535), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_536), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_537), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_538), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_539), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_540), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_541), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_542), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_543), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_544), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_545), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_546), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_547), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_548), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_549), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_550), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_551), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_552), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_553), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_554), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_555), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_556), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_557), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_558), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_559), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_560), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_561), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_562), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_563), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_564), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_565), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_566), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_567), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_568), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_569), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_570), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_571), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_572), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_573), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_574), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_575), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_576), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_577), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_578), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_579), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_580), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_581), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_582), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_583), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_584), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_585), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_586), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_587), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_588), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_589), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_590), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_591), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_592), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_593), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_594), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_595), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_596), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_597), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_598), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_599), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_600), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_601), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_602), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_603), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_604), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_605), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_606), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_607), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_608), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_609), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_610), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_611), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_612), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_613), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_614), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_615), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_616), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_617), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_618), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_619), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_620), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_621), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_622), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_623), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_624), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_625), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_626), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_627), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_628), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_629), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_630), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_631), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_632), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_633), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_634), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_635), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_636), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_637), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_638), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_639), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_640), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_641), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_642), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_643), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_644), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_645), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_646), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_647), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_648), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_649), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_650), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_651), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_652), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_653), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_654), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_655), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_656), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_657), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_658), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_659), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_660), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_661), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_662), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_663), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_664), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_665), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_666), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_667), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_668), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_669), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_670), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_671), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_672), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_673), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_674), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_675), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_676), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_677), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_678), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_679), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_680), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_681), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_682), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_683), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_684), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_685), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_686), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_687), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_688), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_689), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_690), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_691), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_692), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_693), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_694), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_695), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_696), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_697), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_698), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_699), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_700), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_701), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_702), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_703), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_704), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_705), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_706), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_707), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_708), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_709), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_710), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_711), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_712), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_713), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_714), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_715), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_716), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_717), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_718), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_719), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_720), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_721), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_722), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_723), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_724), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_725), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_726), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_727), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_728), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_729), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_730), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_731), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_732), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_733), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_734), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_735), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_736), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_737), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_738), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_739), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_740), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_741), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_742), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_743), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_744), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_745), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_746), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_747), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_748), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_749), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_750), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_751), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_752), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_753), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_754), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_755), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_756), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_757), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_758), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_759), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_760), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_761), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_762), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_763), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_764), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_765), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_766), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_767), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_768), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_769), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_770), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_771), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_772), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_773), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_774), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_775), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_776), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_777), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_778), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_779), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_780), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_781), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_782), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_783), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_784), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_785), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_786), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_787), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_788), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_789), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_790), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_791), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_792), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_793), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_794), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_795), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_796), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_797), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_798), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_799), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_800), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_801), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_802), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_803), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_804), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_805), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_806), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_807), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_808), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_809), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_810), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_811), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_812), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_813), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_814), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_815), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_816), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_817), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_818), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_819), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_820), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_821), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_822), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_823), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_824), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_825), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_826), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_827), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_828), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_829), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_830), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_831), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_832), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_833), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_834), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_835), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_836), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_837), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_838), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_839), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_840), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_841), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_842), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_843), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_844), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_845), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_846), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_847), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_848), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_849), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_850), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_851), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_852), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_853), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_854), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_855), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_856), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_857), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_858), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_859), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_860), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_861), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_862), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_863), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_864), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_865), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_866), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_867), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_868), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_869), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_870), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_871), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_872), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_873), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_874), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_875), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_876), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_877), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_878), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_879), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_880), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_881), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_882), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_883), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_884), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_885), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_886), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_887), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_888), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_889), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_890), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_891), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_892), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_893), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_894), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_895), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_896), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_897), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_898), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_899), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_900), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_901), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_902), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_903), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_904), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_905), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_906), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_907), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_908), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_909), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_910), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_911), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_912), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_913), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_914), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_915), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_916), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_917), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_918), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_919), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_920), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_921), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_922), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_923), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_924), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_925), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_926), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_927), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_928), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_929), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_930), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_931), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_932), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_933), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_934), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_935), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_936), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_937), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_938), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_939), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_940), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_941), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_942), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_943), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_944), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_945), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_946), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_947), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_948), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_949), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_950), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_951), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_952), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_953), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_954), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_955), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_956), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_957), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_958), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_959), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_960), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_961), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_962), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_963), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_964), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_965), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_966), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_967), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_968), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_969), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_970), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_971), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_972), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_973), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_974), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_975), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_976), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_977), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_978), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_979), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_980), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_981), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_982), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_983), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_984), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_985), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_986), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_987), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_988), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_989), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_990), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_991), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_992), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_993), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_994), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_995), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_996), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_997), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_998), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_999), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1000), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1001), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1002), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1003), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1004), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1005), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1006), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1007), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1008), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1009), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1010), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1011), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1012), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1013), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1014), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1015), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1016), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1017), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1018), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1019), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1020), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1021), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1022), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1023), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1024), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1025), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1026), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1027), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1028), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1029), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1030), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1031), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1032), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1033), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1034), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1035), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1036), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1037), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1038), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1039), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1040), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1041), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1042), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1043), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1044), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1045), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1046), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1047), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1048), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1049), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1050), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1051), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1052), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1053), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1054), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1055), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1056), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1057), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1058), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1059), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1060), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1061), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1062), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1063), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1064), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1065), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1066), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1067), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1068), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1069), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1070), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1071), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1072), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1073), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1074), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1075), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1076), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1077), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1078), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1079), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1080), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1081), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1082), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1083), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1084), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1085), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1086), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1087), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1088), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1089), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1090), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1091), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1092), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1093), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1094), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1095), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1096), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1097), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1098), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1099), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1100), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1101), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1102), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1103), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1104), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1105), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1106), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1107), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1108), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1109), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1110), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1111), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1112), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1113), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1114), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1115), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1116), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1117), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1118), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1119), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1120), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1121), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1122), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1123), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1124), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1125), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1126), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1127), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1128), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1129), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1130), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1131), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1132), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1133), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1134), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1135), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1136), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1137), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1138), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1139), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1140), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1141), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1142), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1143), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1144), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1145), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1146), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1147), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1148), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1149), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1150), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1151), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1152), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1153), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1154), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1155), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1156), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1157), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1158), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1159), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1160), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1161), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1162), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1163), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1164), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1165), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1166), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1167), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1168), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1169), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1170), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1171), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1172), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1173), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1174), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1175), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1176), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1177), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1178), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1179), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1180), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1181), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1182), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1183), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1184), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1185), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1186), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1187), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1188), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1189), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1190), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1191), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1192), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1193), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1194), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1195), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1196), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1197), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1198), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1199), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1200), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1201), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1202), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1203), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1204), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1205), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1206), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1207), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1208), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1209), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1210), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1211), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1212), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1213), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1214), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1215), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1216), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1217), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1218), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1219), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1220), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1221), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1222), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1223), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1224), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1225), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1226), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1227), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1228), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1229), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1230), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1231), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1232), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1233), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1234), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1235), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1236), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1237), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1238), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1239), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1240), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1241), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1242), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1243), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1244), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1245), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1246), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1247), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1248), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1249), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1250), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1251), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1252), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1253), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1254), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1255), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1256), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1257), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1258), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1259), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1260), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1261), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1262), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1263), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1264), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1265), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1266), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1267), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1268), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1269), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1270), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1271), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1272), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1273), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1274), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1275), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1276), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1277), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1278), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1279), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1280), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1281), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1282), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1283), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1284), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1285), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1286), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1287), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1288), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1289), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1290), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1291), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1292), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1293), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1294), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1295), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1296), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1297), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1298), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1299), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1300), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1301), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1302), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1303), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1304), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1305), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1306), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1307), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1308), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1309), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1310), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1311), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1312), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1313), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1314), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1315), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1316), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1317), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1318), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1319), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1320), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1321), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1322), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1323), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1324), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1325), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1326), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1327), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1328), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1329), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1330), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1331), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1332), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1333), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1334), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1335), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1336), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1337), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1338), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1339), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1340), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1341), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1342), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1343), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1344), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1345), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1346), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1347), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1348), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1349), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1350), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1351), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1352), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1353), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1354), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1355), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1356), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1357), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1358), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1359), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1360), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1361), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1362), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1363), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1364), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1365), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1366), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1367), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1368), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1369), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1370), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1371), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1372), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1373), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1374), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1375), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1376), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1377), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1378), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1379), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1380), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1381), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1382), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1383), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1384), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1385), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1386), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1387), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1388), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1389), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1390), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1391), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1392), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1393), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1394), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1395), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1396), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1397), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1398), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1399), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1400), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1401), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1402), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1403), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1404), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1405), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1406), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1407), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1408), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1409), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1410), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1411), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1412), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1413), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1414), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1415), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1416), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1417), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1418), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1419), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1420), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1421), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1422), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1423), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1424), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1425), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1426), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1427), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1428), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1429), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1430), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1431), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1432), x, y)
    x = -1
    y += 1
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1433), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1434), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1435), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1436), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1437), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1438), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1439), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1440), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1441), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1442), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1443), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1444), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1445), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1446), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1447), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1448), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1449), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1450), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1451), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1452), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1453), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1454), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1455), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1456), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1457), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1458), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1459), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1460), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1461), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1462), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1463), x, y)
    x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.SPRITE_1464), x, y)