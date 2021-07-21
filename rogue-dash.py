import sys
import warnings
import time
import tcod as libtcod
from constants import StatusType
from engine import Engine

if not sys.warnoptions:
  warnings.simplefilter("ignore")  # Prevent flood of deprecation warnings.

def main():
  engine = Engine()

  while not libtcod.console_is_window_closed():
    # Update all entities
    dt = libtcod.sys_get_last_frame_length()
    status = engine.update(dt)

    if status != StatusType.OK:
      # Upload score to game server
      #engine.upload_score()

      # Fade out
      if status == StatusType.QUIT:
        engine.fadeOut(nframes = 12)
        break
      else:
        engine.fadeOut()

    # Render all entities, equipment and items
    engine.render()

  # Upload score to game server
  #engine.upload_score()

  # Fade out
  if libtcod.console_is_window_closed():
    engine.fadeOut(nframes = 12)

if __name__ == '__main__':
  main()
