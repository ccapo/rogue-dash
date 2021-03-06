import tcod as libtcod

from engine import Engine
from constants import ScorecardType
from handlers import handle_keys
from client import upload_score
from render import clear_all, render_all

def main():
  engine = Engine()

  while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, engine.key, engine.mouse)

    render_all(engine.con, engine.entities, engine.map, engine.screen_width, engine.screen_height, engine.colours)
    libtcod.console_flush()

    clear_all(engine.con, engine.entities)

    action = handle_keys(engine.key)

    move = action.get('move')
    exit = action.get('exit')
    fullscreen = action.get('fullscreen')

    if move:
      dx, dy = move
      if not engine.map.is_blocked(engine.player.x + dx, engine.player.y + dy):
        engine.player.move(dx, dy)

    if exit:
      scorecard = {'0x0A': 1, '0x0B': 2, '0x0C': 3}
      upload_score(scorecard)
      return True

    if fullscreen:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

if __name__ == '__main__':
  main()
