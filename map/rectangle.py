class Rectangle():
  def __init__(self, x, y, w, h, map_width):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h
    self.vacant = [s + map_width*t for t in range(self.y1, self.y2) for s in range(self.x1, self.x2)]

  def center(self):
    center_x = int((self.x1 + self.x2) / 2)
    center_y = int((self.y1 + self.y2) / 2)
    return (center_x, center_y)

  def intersect(self, other):
    # returns true if this rectangle intersects with another one
    return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

  def __lt__(self, other):
    # returns true if this rectangle is above and to the left of ther other
    return (self.y1, self.x1) < (other.y1, other.x1)