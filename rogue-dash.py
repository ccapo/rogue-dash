import tcod as libtcod

def main():
  screen_width = 80
  screen_height = 50

  libtcod.console_set_custom_font('data/fonts/arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

  libtcod.console_init_root(screen_width, screen_height, 'rogue-dash (2021 7DRL)', False)

  while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_put_char(0, 1, 1, '@', libtcod.BKGND_NONE)
    libtcod.console_flush()

    key = libtcod.console_check_for_keypress()

    if key.vk == libtcod.KEY_ESCAPE:
      return True


if __name__ == '__main__':
  main()
