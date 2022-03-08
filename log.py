import tcod as libtcod
import textwrap3

class Log:
  def __init__(self, x, width, height):
    self.messages = []
    self.x = x
    self.width = width
    self.height = height

  def add(self, message, colour = libtcod.white):
    # Split the message if necessary, among multiple lines
    new_msg_lines = textwrap3.wrap(message, self.width)

    for line in new_msg_lines:
      # If the buffer is full, remove the first line to make room for the new one
      if len(self.messages) == self.height:
        del self.messages[0]

      # Add the new line as a Message object, with the text and the colour
      self.messages.append({'text': line, 'colour': colour})

  def clear(self):
    self.messages = []
