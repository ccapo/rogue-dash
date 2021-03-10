import tcod as libtcod

def render_bar(panel, x, y, total_width, name, value, maximum, bar_colour, back_colour):
  bar_width = int(float(value) / maximum * total_width)

  libtcod.console_set_default_background(panel, back_colour)
  libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

  libtcod.console_set_default_background(panel, bar_colour)
  if bar_width > 0:
    libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

  libtcod.console_set_default_foreground(panel, libtcod.white)
  libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))

def render_all(con, panel, map, log, entities, screen_width, screen_height, bar_width, panel_height, panel_yoffset, colours):
  player = entities[0]

  # Update camera offset
  map.move_camera(map.progress_yoffset)

  # Draw all the tiles visble from the camera
  for y in range(map.camera_yoffset, map.camera_height + map.camera_yoffset + 1):
    for x in range(map.camera_width):
      wall = map.tiles[x][y].block_sight

      if wall:
        libtcod.console_set_char_background(con, x, y - map.camera_yoffset, colours.get('dark_wall'), libtcod.BKGND_SET)
      else:
        libtcod.console_set_char_background(con, x, y - map.camera_yoffset, colours.get('dark_ground'), libtcod.BKGND_SET)

  # Draw all entities in the list in reverse order (i.e. items, creatures, player)
  for entity in reversed(entities):
    draw_entity(con, map, entity)

  libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

  libtcod.console_set_default_background(panel, libtcod.black)
  libtcod.console_clear(panel)

  # Print the game messages, one line at a time
  y = 1
  for message in log.messages:
    libtcod.console_set_default_foreground(panel, message.colour)
    libtcod.console_print_ex(panel, log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
    y += 1

  render_bar(panel, 1, 1, bar_width, 'HP', player.stats.hp, player.stats.hpmax, libtcod.light_red, libtcod.darker_red)

  #libtcod.console_set_default_foreground(panel, libtcod.light_gray)
  #libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
  #                         get_names_under_mouse(mouse, entities, fov_map))

  libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_yoffset)

def clear_all(con, map, entities):
  for entity in entities:
    clear_entity(con, map, entity)

def draw_entity(con, map, entity):
  libtcod.console_set_default_foreground(con, entity.colour)
  libtcod.console_put_char(con, entity.x, entity.y - map.camera_yoffset, entity.sym, libtcod.BKGND_NONE)

def clear_entity(con, map, entity):
  # erase the character that represents this object
  libtcod.console_put_char(con, entity.x, entity.y - map.camera_yoffset, ' ', libtcod.BKGND_NONE)