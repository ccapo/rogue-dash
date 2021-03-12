import sys
import warnings
import time
import tcod as libtcod
from engine import Engine

if not sys.warnoptions:
  warnings.simplefilter("ignore")  # Prevent flood of deprecation warnings.

def main():
  engine = Engine()
  status = True

  while not libtcod.console_is_window_closed() and status:
    # Update all entities
    status = engine.update()

    # Render all entities, equipment and items
    engine.render()

  # Upload score to game server
  engine.upload_score()

  # Fade out
  if not status:
    for i in range(25):
      fade = 255*(24 - i)//24
      libtcod.console_set_fade(fade, libtcod.black)
      libtcod.console_flush()
      time.sleep(0.05)

if __name__ == '__main__':
  main()
