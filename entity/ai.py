class AI:
  def __init__(self, type = None):
    self.type = type

  def update(self):
    return 'updating (' + self.type + ')'