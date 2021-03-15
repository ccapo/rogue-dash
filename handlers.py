import tcod as libtcod

def handle_keys(key):
  # Movement keys
  if key.vk == libtcod.KEY_UP or key.c in (ord('W'), ord('w')):
    return {'move': (0, -1)}
  elif key.vk == libtcod.KEY_LEFT or key.c in (ord('A'), ord('a')):
    return {'move': (-1, 0)}
  elif key.vk == libtcod.KEY_DOWN or key.c in (ord('S'), ord('s')):
    return {'move': (0, 1)}
  elif key.vk == libtcod.KEY_RIGHT or key.c in (ord('D'), ord('d')):
    return {'move': (1, 0)}

  if key.vk == libtcod.KEY_DELETE:
    # Delete: toggle full screen
    return {'fullscreen': True}

  elif key.vk == libtcod.KEY_ENTER:
    # Enter: Perform action
    return {'action': True}

  elif key.vk == libtcod.KEY_ESCAPE:
    # Exit the game
    return {'exit': True}

  # No key was pressed
  return {}