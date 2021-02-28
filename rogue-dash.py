import tcod as libtcod

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

  player = Entity(int(screen_width / 2), int(screen_height / 2), '@', libtcod.white)
  npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), '@', libtcod.yellow)
  entities = [npc, player]

  libtcod.console_set_custom_font('data/fonts/arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

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
