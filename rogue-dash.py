import sys
import warnings
import tcod as libtcod

from engine import Engine
from constants import ScorecardType
from handlers import handle_keys
from client import upload_score
from render import clear_all, render_all

if not sys.warnoptions:
  warnings.simplefilter("ignore")  # Prevent flood of deprecation warnings.

def main():
  engine = Engine()
  elapsed = -1.0

  while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, engine.key, engine.mouse)

    # Update progress offset
    elapsed += libtcod.sys_get_last_frame_length()
    if elapsed > engine.delay_threshold():
      elapsed = 0.0
      engine.map.progress_yoffset -= 1
      if engine.map.progress_yoffset <= 0:
        engine.map.progress_yoffset = 0

    render_all(engine.con, engine.panel, engine.map, engine.log, engine.entities, engine.screen_width, engine.screen_height, engine.bar_width, engine.panel_height, engine.panel_yoffset, engine.colours)
    libtcod.console_flush()

    clear_all(engine.con, engine.map, engine.entities)

    action = handle_keys(engine.key)

    move = action.get('move')
    exit = action.get('exit')
    fullscreen = action.get('fullscreen')

    if move:
      dx, dy = move
      dest_x = engine.player.x + dx
      dest_y = engine.player.y + dy
      if not engine.map.is_blocked(dest_x, dest_y):
        target = engine.get_blocking_entities(dest_x, dest_y)
        if target is not None:
          print('You kick the ' + target.name + ' in the shins, much to its annoyance!')
        else:
          engine.player.move(dx, dy)

    if exit:
      break

    if fullscreen:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

  # Upload score to game server
  upload_score(engine.scorecard)

if __name__ == '__main__':
  main()
