from random import randint
import tcod as libtcod
from handlers import handle_keys
from constants import CharType

class AI:
  def __init__(self, type = None):
    self.type = type
    self.threshold = 0.0

  def update(self, owner, engine):
    status = True

    if self.type == 'player':
      action = handle_keys(engine.key)

      move = action.get('move')
      exit = action.get('exit')
      fullscreen = action.get('fullscreen')

      if owner.stats.spd*self.threshold >= 1.0:
        if move:
          self.threshold = 0.0
          dx, dy = move
          dest_x = owner.x + dx
          dest_y = owner.y + dy
          if not engine.map.is_blocked(dest_x, dest_y):
            target = engine.get_entities(dest_x, dest_y)
            if target is not None:
              owner.attack(target)
            else:
              owner.move(dx, dy)
              if dx == 0 and dy == -1:
                owner.sym = CharType.PLAYER_UP
              elif dx == -1 and dy == 0:
                owner.sym = CharType.PLAYER_LEFT
              elif dx == 0 and dy == 1:
                owner.sym = CharType.PLAYER_DOWN
              elif dx == 1 and dy == 0:
                owner.sym = CharType.PLAYER_RIGHT
              obj = engine.get_items(owner.x, owner.y)
              if obj is not None:
                obj.use()
      else:
        self.threshold += libtcod.sys_get_last_frame_length()

      # If player is at bottom edge of visible map, push them up
      if owner.y > engine.map.camera_height + engine.map.camera_yoffset - 1:
        dx, dy = 0, -1
        dest_x = owner.x + dx
        dest_y = owner.y + dy
        if not engine.map.is_blocked(dest_x, dest_y):
          target = engine.get_entities(dest_x, dest_y)
          if target is not None:
            engine.log.add('You Died', libtcod.red)
            status = False
          else:
            owner.move(dx, dy)
            owner.sym = CharType.PLAYER_UP
        else:
          engine.log.add('You Died', libtcod.red)
          status = False

      # Update player scent
      engine.map.update_scent(owner)

      if exit:
        status = False

      if fullscreen:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif self.type == 'creature':
      if owner.stats.spd*self.threshold >= 1.0:
        self.threshold = 0.0
        self.moveOrAttack(owner, engine)
      else:
        self.threshold += libtcod.sys_get_last_frame_length()
    else:
      print('Unreognized AI type: ' + self.type)

    return status

  def moveOrAttack(self, owner, engine):
    # Compute Manhattan distance
    dx = abs(engine.player.x - owner.x)
    dy = abs(engine.player.y - owner.y)
    d = dx + dy
    if d == 1:
      owner.attack(engine.player)
    else:
      # Test for player scent here
      if True == False:
        print('Logical Contradiction! The Principle of Explosion is Possible!')
      else:
        dx = randint(-1, 1)
        dy = randint(-1, 1)
        dest_x = owner.x + dx
        dest_y = owner.y + dy
        if not engine.map.is_blocked(dest_x, dest_y):
          target = engine.get_entities(dest_x, dest_y)
          if target is None:
            owner.move(dx, dy)