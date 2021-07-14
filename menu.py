import tcod as libtcod

class Menu:
  def __init__(self, screen_width, screen_height):
    # Define screen width and height
    self.screen_width = screen_width
    self.screen_height = screen_height

    self.name = ''
    self.score = 0
    self.highscore = 0

    self.title = 'Welcome To Rogue Dash!'
    self.options = ['Movement:     WASD or Arrow Keys',
                    'Dash:         Spacebar',
                    'Action:       Enter',
                    'Fullscreen:   Delete',
                    'Quit:         Escape']

  def update(self, record):
    self.name = record.name
    self.score = record.score
    self.highscore = record.highscore

  def render(self, con):
    x = self.screen_width // 2 - len(self.title) // 2; y = self.screen_height // 3
    libtcod.console_print_ex(con, x, y, libtcod.BKGND_NONE, libtcod.LEFT, self.title)

    x = self.screen_width // 2 - len(self.options[0]) // 2; y = self.screen_height // 2
    for opt in self.options:
      x = self.screen_width // 2 - len(self.options[0]) // 2; y += 1
      libtcod.console_print_ex(con, x, y, libtcod.BKGND_NONE, libtcod.LEFT, opt)

    # Display name and high score when present
    if self.name != '' and self.highscore > 0:
      x = self.screen_width // 2 - len(self.options[0]) // 2; y += 4
      libtcod.console_print_ex(con, x, y, libtcod.BKGND_NONE, libtcod.LEFT, "Player Stats")
      x = self.screen_width // 2 - len(self.options[0]) // 2; y += 1
      libtcod.console_print_ex(con, x, y, libtcod.BKGND_NONE, libtcod.LEFT, "Name: {}".format(self.name))
      x = self.screen_width // 2 - len(self.options[0]) // 2; y += 1
      libtcod.console_print_ex(con, x, y, libtcod.BKGND_NONE, libtcod.LEFT, "Recent Score: {}".format(self.score))
      x = self.screen_width // 2 - len(self.options[0]) // 2; y += 1
      libtcod.console_print_ex(con, x, y, libtcod.BKGND_NONE, libtcod.LEFT, "High Score:   {}".format(self.highscore))