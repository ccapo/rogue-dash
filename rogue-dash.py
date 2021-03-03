import tcod as libtcod

from tiles import CharType
from entity import Entity
from handlers import handle_keys
from map.map import Map
from client import upload_score
from render import clear_all, render_all

def main():
  screen_width = 80
  screen_height = 50
  map_width = screen_width
  map_height = screen_height - 5

  colors = {
    'dark_wall': libtcod.Color(0, 0, 100),
    'dark_ground': libtcod.Color(50, 50, 150)
  }

  libtcod.console_set_custom_font('data/fonts/arial16x16-ext2.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 46)

  # Assign extra ascii keys
  x = -1
  y = 8
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_STAIRS_UP), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_STAIRS_DOWN), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_HOLE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_WATER_01), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_WATER_02), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_LAVA_01), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_LAVA_02), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CHEST_OPEN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CHEST_CLOSED), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_POTION_YELLOW), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_POTION_RED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_POTION_GREEN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_POTION_BLUE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_KEY), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RING_RED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RING_GREEN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RING_BLUE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RING_RED_BIG), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RING_GREEN_BIG), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RING_BLUE_BIG), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHIELD_BROWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHIELD_GREY), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHIELD_GOLD), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SWORD_BASIC), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SWORD_STEEL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SWORD_GOLD), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ARMOUR_BROWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ARMOUR_YELLOW), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ARMOUR_RED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ARMOUR_GREEN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ARMOUR_BLUE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ARMOUR_MITHRIL), x, y)
  x = -1
  y += 1

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CHARGEBAR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PLAYER_RIGHT), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PLAYER_DOWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PLAYER_LEFT), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PLAYER_UP), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GUARDIAN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_KEEPER), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PERSON_MALE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PERSON_FEMALE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GUARD), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_WARLOCK_PURPLE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_NECROMANCER_APPENTICE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_NECROMANCER_MASTER), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DARKELF_ARCHER), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DARKELF_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DARKELF_MAGE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DWARF_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DWARF_AXEBEARER), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DWARF_MAGE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DWARF_HERO), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_UNDEAD_DWARF_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_UNDEAD_DWARF_AXEBEARER), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_UNDEAD_DWARF_MAGE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_UNDEAD_DWARF_HERO), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GOBLIN_PEON), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GOBLIN_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GOBLIN_MAGE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_IMP_BLUE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_IMP_RED), x, y)
  x = -1
  y += 1

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORGE_PEON_GREEN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORGE_WARRIOR_GREEN), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORGE_PEON_RED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORGE_WARRIOR_RED), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SKELETON_PEON), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SKELETON_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SKELETON_HERO), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SKELETON_MAGE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SPRITE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORC_PEON), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORC_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORC_HERO), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_ORC_MAGE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMON_PEON), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMON_HERO), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMON_MAGE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLAYER_WARRIOR), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLAYER_MAGE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SKULL), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GOLEM_GREY), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GOLEM_BROWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_GOLEM_RED), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SLIME_BROWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SLIME_GREEN), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_EYEBALL), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_VERMIN_BROWN), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SNAKE_GREEN), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_RUBBLE_PILE), x, y)
  x = -1
  y += 1

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SCORPIAN_YELLOW), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SCORPIAN_BLACK), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SPIDER_BLACK), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SPIDER_RED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SPIDER_GREEN), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PYTHON_RED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PYTHON_BROWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_PYTHON_YELLOW), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BAT_BROWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BAT_BLUE), x, y)

  # Environment Tiles
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_A), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_B), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_C), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_D), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_E), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_F), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TREE_G), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHRUB_A), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHRUB_B), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHRUB_C), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SHRUB_D), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MUSHROOM), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLOWERS_WHITE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLOWERS_BLUE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TEMPLE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TOWN), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CAVE), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BED), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_TABLE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BOOKCASE), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CHAIR_RIGHT), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CHAIR_LEFT), x, y)
  x = -1
  y += 1

  # Minor Bosses (Upper Portion)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_WHITE_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_WHITE_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_RED_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_RED_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CYCLOPS_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CYCLOPS_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_RED_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_RED_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_YELLOW_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_YELLOW_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREEN_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREEN_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_BLUE_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_BLUE_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREY_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREY_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MINOTAUR_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MINOTAUR_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_LIZARD_GIANT_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_LIZARD_GIANT_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MEDUSA_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MEDUSA_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLYING_BRAIN_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLYING_BRAIN_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SLIMELORD_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SLIMELORD_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHOLDER_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHOLDER_UR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHEMOTH_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHEMOTH_UR), x, y)

  # Final Boss (Upper Portion)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FINAL_BOSS_UL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FINAL_BOSS_UR), x, y)
  x = -1
  y += 1

  # Minor Bosses (Lower Portion)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_WHITE_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_WHITE_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_RED_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DEMONLORD_RED_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CYCLOPS_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_CYCLOPS_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_RED_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_RED_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_YELLOW_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_YELLOW_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREEN_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREEN_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_BLUE_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_BLUE_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREY_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_DRAGON_LARGE_GREY_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MINOTAUR_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MINOTAUR_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_LIZARD_GIANT_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_LIZARD_GIANT_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MEDUSA_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_MEDUSA_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLYING_BRAIN_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FLYING_BRAIN_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SLIMELORD_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_SLIMELORD_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHOLDER_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHOLDER_LR), x, y)

  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHEMOTH_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_BEHEMOTH_LR), x, y)

  # Final Boss (Lower Portion)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FINAL_BOSS_LL), x, y)
  x += 1; libtcod.console_map_ascii_code_to_font(int(CharType.CHAR_FINAL_BOSS_LR), x, y)

  player = Entity(int(screen_width / 2), int(screen_height / 2), '@', libtcod.white)
  npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), CharType.CHAR_KEEPER, libtcod.white)
  entities = [npc, player]

  libtcod.console_init_root(screen_width, screen_height, 'rogue-dash (2021 7DRL)', False)

  con = libtcod.console_new(screen_width, screen_height)

  map = Map(map_width, map_height)

  key = libtcod.Key()
  mouse = libtcod.Mouse()

  while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

    render_all(con, entities, map, screen_width, screen_height, colors)
    libtcod.console_flush()

    clear_all(con, entities)

    action = handle_keys(key)

    move = action.get('move')
    exit = action.get('exit')
    fullscreen = action.get('fullscreen')

    if move:
      dx, dy = move
      if not map.is_blocked(player.x + dx, player.y + dy):
        player.move(dx, dy)

    if exit:
      scorecard = {'0x0A': 1, '0x0B': 2, '0x0C': 3}
      upload_score(scorecard)
      return True

    if fullscreen:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
  main()
