import math
import random
from map.tile import Tile

class CellularAutomata:
  '''
  Rather than implement a traditional cellular automata, I 
  decided to try my hand at a method discribed by "Evil
  Scientist" Andy Stobirski that I recently learned about
  on the Grid Sage Games blog.
  '''
  def __init__(self, mapWidth, mapHeight):
    self.mapWidth = mapWidth
    self.mapHeight = mapHeight

    self.iterations = 30000
    self.neighbors = 4 # number of neighboring walls for this cell to become a wall
    self.wallProbability = 0.50 # the initial probability of a cell becoming a wall, recommended to be between .35 and .55

    self.ROOM_MIN_SIZE = 16 # size in total number of cells, not dimensions
    self.ROOM_MAX_SIZE = 500 # size in total number of cells, not dimensions

    self.smoothEdges = True
    self.smoothing =  1

  def generateLevel(self):
    # Creates an empty 2D array or clears existing array
    self.caves = []

    self.tiles = [[Tile() for y in range(self.mapHeight)] for x in range(self.mapWidth)]

    self.randomFillMap()
    
    self.createCaves()

    self.getCaves()

    self.connectCaves()

    self.cleanUpMap()

    return self.tiles

  def randomFillMap(self):
    for y in range(1, self.mapHeight - 1):
      for x in range(1, self.mapWidth - 1):
        if random.random() >= self.wallProbability:
          self.tiles[x][y].blocked = False

  def createCaves(self):
    # ==== Create distinct caves ====
    for i in range(self.iterations):
      # Pick a random point with a buffer around the edges of the map
      x = random.randint(1,self.mapWidth-2) #(2,self.mapWidth-3)
      y = random.randint(1,self.mapHeight-2) #(2,self.mapHeight-3)

      # if the cell's neighboring walls > self.neighbors, set it to 1
      if self.getAdjacentWalls(x,y) > self.neighbors:
        self.tiles[x][y].blocked = True
      # or set it to 0
      elif self.getAdjacentWalls(x,y) < self.neighbors:
        self.tiles[x][y].blocked = False

    # ==== Clean Up Map ====
    self.cleanUpMap()

  def cleanUpMap(self):
    if (self.smoothEdges):
      for i in range(5):
        # Look at each cell individually and check for smoothness
        for x in range(1,self.mapWidth-1):
          for y in range(1,self.mapHeight-1):
            if (self.tiles[x][y].blocked == True) and (self.getAdjacentWallsSimple(x,y) <= self.smoothing):
              self.tiles[x][y].blocked = False

  def createTunnel(self,offset,end_offset,endCave):
    # run a heavily weighted random Walk 
    # from point1 to point1
    x_end = end_offset % self.mapWidth
    y_end = end_offset // self.mapWidth
    x = offset % self.mapWidth
    y = offset // self.mapWidth
    while offset not in endCave:
      # ==== Choose Direction ====
      north = 1.0
      south = 1.0
      east = 1.0
      west = 1.0

      weight = 1

      # weight the random walk against edges
      if x < x_end:
        east += weight
      elif x > x_end:
        west += weight

      if y < y_end:
        south += weight
      elif y > y_end:
        north += weight

      # normalize probabilities so they form a range from 0 to 1
      total = north+south+east+west
      north /= total
      south /= total
      east /= total
      west /= total

      # choose the direction
      choice = random.random()
      if 0 <= choice < north:
        dx = 0
        dy = -1
      elif north <= choice < (north+south):
        dx = 0
        dy = 1
      elif (north+south) <= choice < (north+south+east):
        dx = 1
        dy = 0
      else:
        dx = -1
        dy = 0

      # ==== Walk ====
      # check colision at edges
      if (0 < x+dx < self.mapWidth-1) and (0 < y+dy < self.mapHeight-1):
        x += dx
        y += dy
        offset = x + self.mapWidth*y
        if self.tiles[x][y].blocked == True:
          self.tiles[x][y].blocked = False

  def getAdjacentWallsSimple(self, x, y): # finds the walls in four directions
    wallCounter = 0
    if (self.tiles[x][y-1].blocked == True): # Check north
      wallCounter += 1
    if (self.tiles[x][y+1].blocked == True): # Check south
      wallCounter += 1
    if (self.tiles[x-1][y].blocked == True): # Check west
      wallCounter += 1
    if (self.tiles[x+1][y].blocked == True): # Check east
      wallCounter += 1

    return wallCounter

  def getAdjacentWalls(self, tileX, tileY): # finds the walls in 8 directions
    pass
    wallCounter = 0
    for x in range(tileX-1, tileX+2):
      for y in range(tileY-1, tileY+2):
        if (self.tiles[x][y].blocked == True):
          if (x != tileX) or (y != tileY): # exclude (tileX,tileY)
            wallCounter += 1
    return wallCounter

  def getCaves(self):
    # locate all the caves within self.tiles and store them in self.caves
    for x in range(self.mapWidth):
      for y in range(self.mapHeight):
        if self.tiles[x][y].blocked == False:
          self.floodFill(x,y)

    for cave in self.caves:
      for offset in cave:
        xp = offset % self.mapWidth
        yp = offset // self.mapWidth
        self.tiles[xp][yp].blocked = False

  def floodFill(self,x,y):
    '''
    flood fill the separate regions of the level, discard
    the regions that are smaller than a minimum size, and 
    create a reference for the rest.
    '''
    cave = []
    offset = x + self.mapWidth*y
    toBeFilled = [offset]
    while toBeFilled:
      offset = toBeFilled.pop()
      
      if offset not in cave:
        cave.append(offset)
        
        xp = offset % self.mapWidth
        yp = offset // self.mapWidth
        self.tiles[xp][yp].blocked = True
        
        # check adjacent cells
        dx = [-1, 0, 1,  0]
        dy = [ 0, 1, 0, -1]
        for i in range(4):
          xpp = xp + dx[i]
          ypp = yp + dy[i]
          off = xpp + self.mapWidth*ypp
          if self.tiles[xpp][ypp].blocked == False and off not in toBeFilled and off not in cave:
            toBeFilled.append(off)

    if len(cave) >= self.ROOM_MIN_SIZE:
      self.caves.append(cave)

  def connectCaves(self):
    for i in range(len(self.caves)):
      minDistance = 1.0e9
      closest_offset = None
      offseti = self.caves[i][0]
      for j in range(i+1,len(self.caves)):
        offsetj = self.caves[j][0]
        dij = self.distance(offseti,offsetj)
        if (dij < minDistance):
          minDistance = dij
          closest_offset = offsetj

      if closest_offset != None:
        self.createTunnel(closest_offset,offseti,self.caves[i])

  def distance(self,o1,o2):
    x1 = o1 % self.mapWidth
    y1 = o1 // self.mapWidth
    x2 = o2 % self.mapWidth
    y2 = o2 // self.mapWidth
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)