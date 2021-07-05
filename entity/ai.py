from random import randint
import tcod as libtcod
from handlers import handle_keys
from constants import CharType

class AI:
  def __init__(self, type = None, scent_threshold = 0.0625):
    self.type = type
    self.scent_threshold = scent_threshold
    self.move_elapsed = 0.0
    self.dash_elapsed = 0.0
    self.consume_elapsed = 0.0

  def update(self, owner, engine):
    status = True

    if self.type == 'player':
      action = handle_keys(engine.key)

      move = action.get('move')
      dash = action.get('dash')
      stairs = action.get('stairs')
      quit = action.get('quit')
      fullscreen = action.get('fullscreen')

      if owner.stats.spd*self.move_elapsed >= 1.0:
        if move:
          self.move_elapsed = 0.0
          dx, dy = move
          self.playerUpdate(owner, engine, dx, dy)
      else:
        self.move_elapsed += libtcod.sys_get_last_frame_length()

      # Dash
      if owner.stats.spd*self.dash_elapsed >= 50.0:
        if dash:
          self.dash_elapsed = 0.0
          dx = 0
          dy = 0
          if owner.sym == CharType.PLAYER_UP:
            dy = -1
          elif owner.sym == CharType.PLAYER_LEFT:
            dx = -1
          elif owner.sym == CharType.PLAYER_DOWN:
            dy = 1
          elif owner.sym == CharType.PLAYER_RIGHT:
            dx = 1

          for i in range(5):
            if not self.playerUpdate(owner, engine, dx, dy): break
      else:
        self.dash_elapsed += libtcod.sys_get_last_frame_length()

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

      if stairs:
        stairs = engine.get_exit(owner.x, owner.y)
        if stairs is not None:
          engine.next_stage = True
          status = True

      if quit:
        status = False

      if fullscreen:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif self.type == 'creature':
      if owner.stats.spd*self.move_elapsed >= 1.0:
        self.move_elapsed = 0.0
        player_died = self.moveOrAttack(owner, engine)
        if player_died == True:
          engine.log.add('You Died', libtcod.red)
          status = False
      else:
        self.move_elapsed += libtcod.sys_get_last_frame_length()
    else:
      print('Unreognized AI type: ' + self.type)

    return status

  def moveOrAttack(self, owner, engine):
    # Compute Manhattan distance
    dx = abs(engine.player.x - owner.x)
    dy = abs(engine.player.y - owner.y)
    d = dx + dy
    if d == 1:
      return owner.attack(engine.player, engine)
    else:
      # Search for the largest scent in cardinal direction *only*
      iz = -1
      scentMax = -1.0
      dx = ( 0, -1, 0, 1)
      dy = (-1,  0, 1, 0)
      for z in range(4):
        scent = engine.map.tiles[owner.x + dx[z]][owner.y + dy[z]].current_scent
        if scent > scentMax:
          scentMax = scent
          iz = z

      # If scent is less then creature's threshold, ignore
      if scentMax <= self.scent_threshold:
        iz = -1

      # Decide if we are following the player or moving randomly
      if iz != -1:
        dest_x = owner.x + dx[iz]
        dest_y = owner.y + dy[iz]
      else:
        iz = 0
        dx = (randint(-1, 1),)
        dy = (randint(-1, 1),)
        dest_x = owner.x + dx[iz]
        dest_y = owner.y + dy[iz]

      # If the destination is not blocked or another entity, move in the direction of the player
      if not engine.map.is_blocked(dest_x, dest_y):
        target = engine.get_entities(dest_x, dest_y)
        if target is None:
          owner.move(dx[iz], dy[iz])
      return False

  def playerUpdate(self, owner, engine, dx, dy):
    dest_x = owner.x + dx
    dest_y = owner.y + dy
    if not engine.map.is_blocked(dest_x, dest_y):
      target = engine.get_entities(dest_x, dest_y)
      if target is not None:
        owner.attack(target, engine)
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
          used = obj.use(owner)
          if used == True:
            engine.items.remove(obj)
      return True
    else:
      return False