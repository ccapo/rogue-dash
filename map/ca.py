import math
import random
from map.tile import Tile

class CellularAutomata:
  '''
  Andy Stobirski's cellular automata algorithm from Grid Sage Games blog.
  '''
  def __init__(self, mapWidth, mapHeight):
    self.mapWidth = mapWidth
    self.mapHeight = mapHeight

    # Number of iterations when creating caves
    self.iterations = 30000

    # Number of neighboring walls for this cell to become a wall
    self.neighbors = 4

    # The initial probability of a cell becoming a wall, recommended to be between .35 and .55
    self.wallProbability = 0.5

    # Size in total number of cells, not dimensions
    self.ROOM_MIN_SIZE = 16

    # Size in total number of cells, not dimensions
    self.ROOM_MAX_SIZE = 500

    self.smoothEdges = True
    self.smoothing =  1

  # Generate a map
  def generateLevel(self):
    self.caves = []
    self.tiles = [[Tile() for y in range(self.mapHeight)] for x in range(self.mapWidth)]

    # Start with randomly filled map
    self.randomFillMap()
    
    # Apply cellular automata rules iteratively
    self.createCaves()

    # Create a cavity where the player will start
    self.createCavity()

    # Locate all the isolated caves, discarding small and large caves
    self.getCaves()

    # Connect caves via tunnels
    self.connectCaves()

    # Clean up map by smoothing endges
    self.cleanUpMap()

    return self.tiles

  def sealLevel(self):
    y = 0
    for x in range(self.mapWidth):
      self.tiles[x][y].blocked = True
    y = self.mapHeight - 1
    for x in range(self.mapWidth):
      self.tiles[x][y].blocked = True
    x = 0
    for y in range(self.mapHeight):
      self.tiles[x][y].blocked = True
    x = self.mapWidth - 1
    for y in range(self.mapHeight):
      self.tiles[x][y].blocked = True

  # Randomly populate map
  def randomFillMap(self):
    for y in range(2, self.mapHeight - 2):
      for x in range(2, self.mapWidth - 2):
        if random.random() >= self.wallProbability:
          self.tiles[x][y].blocked = False

    self.sealLevel()

  def createCaves(self):
    for i in range(self.iterations):
      # Pick a random point with a buffer around the edges of the map
      x = random.randint(2, self.mapWidth - 3)
      y = random.randint(2, self.mapHeight - 3)

      # If the cell's neighboring walls > self.neighbors, set blocked to true
      if self.getAdjacentWalls(x,y) > self.neighbors:
        self.tiles[x][y].blocked = True
      # Or set blocked to false
      elif self.getAdjacentWalls(x,y) < self.neighbors:
        self.tiles[x][y].blocked = False

    self.sealLevel()

  # Clean Up Map
  def cleanUpMap(self):
    if self.smoothEdges:
      for i in range(5):
        # Look at each cell individually and check for smoothness
        for x in range(2, self.mapWidth - 2):
          for y in range(2, self.mapHeight - 2):
            if (self.tiles[x][y].blocked == True) and (self.getAdjacentWallsSimple(x,y) <= self.smoothing):
              self.tiles[x][y].blocked = False

  # Create a tunnel from offset to end_offset using a heavily weighted random walk
  def createTunnel(self,offset,end_offset,endCave):
    x_end = end_offset % self.mapWidth
    y_end = end_offset // self.mapWidth
    x = offset % self.mapWidth
    y = offset // self.mapWidth
    while offset not in endCave:
      # Choose Direction
      north = 1.0
      south = 1.0
      east = 1.0
      west = 1.0
      weight = 1

      # Weight the random walk against edges
      if x < x_end:
        east += weight
      elif x > x_end:
        west += weight

      if y < y_end:
        south += weight
      elif y > y_end:
        north += weight

      # Normalize probabilities
      total = north+south+east+west
      north /= total
      south /= total
      east /= total
      west /= total

      # Choose the direction
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

      # Walk, avoiding boundaries
      if (1 < x + dx < self.mapWidth - 2) and (1 < y + dy < self.mapHeight - 2):
        x += dx
        y += dy
        offset = x + self.mapWidth*y
        if self.tiles[x][y].blocked == True:
          self.tiles[x][y].blocked = False

  # Create a cavity where the player will start
  def createCavity(self):
    # Height of starting region
    hmax = 7

    # Fill in the region first
    for h in range(hmax):
      y = self.mapHeight - 2 - h
      for x in range(self.mapWidth):
        self.tiles[x][y].blocked = True

    # Excavate starting location
    for h in range(hmax):
      y = self.mapHeight - 2 - h
      xmin = 1 + self.mapWidth // 4 + (hmax // 2 - h)
      xmax = 3 * self.mapWidth // 4 - 1 - (hmax // 2 - h)
      for x in range(xmin, xmax):
        self.tiles[x][y].blocked = False

    self.sealLevel()

  # Finds the walls in four directions
  def getAdjacentWallsSimple(self, x, y):
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

  # Finds the walls in 8 directions
  def getAdjacentWalls(self, tileX, tileY):
    wallCounter = 0
    for x in range(tileX-1, tileX+2):
      for y in range(tileY-1, tileY+2):
        if self.tiles[x][y].blocked == True:
          # Exclude reference location
          if (x != tileX) or (y != tileY):
            wallCounter += 1
    return wallCounter

  # Locate all the caves within self.tiles and store them in self.caves
  def getCaves(self):
    for x in range(self.mapWidth):
      for y in range(self.mapHeight):
        if self.tiles[x][y].blocked == False:
          self.floodFill(x,y)

    for cave in self.caves:
      for offset in cave:
        xp = offset % self.mapWidth
        yp = offset // self.mapWidth
        if xp >= 1 and xp <= self.mapWidth - 2 and yp >= 1 and yp <= self.mapHeight - 2:
          self.tiles[xp][yp].blocked = False

  def floodFill(self,x,y):
    '''
    Flood fill the separate regions of the level, discard
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
        
        # Check adjacent cells
        dx = [-1, 0, 1,  0]
        dy = [ 0, 1, 0, -1]
        for i in range(len(dx)):
          xpp = xp + dx[i]
          ypp = yp + dy[i]
          off = xpp + self.mapWidth*ypp
          if self.tiles[xpp][ypp].blocked == False and off not in toBeFilled and off not in cave:
            toBeFilled.append(off)

    if len(cave) >= self.ROOM_MIN_SIZE:
      self.caves.append(cave)

  # Connect the closest pairs of caves
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

  # Distance between two offsets
  def distance(self,o1,o2):
    x1 = o1 % self.mapWidth
    y1 = o1 // self.mapWidth
    x2 = o2 % self.mapWidth
    y2 = o2 // self.mapWidth
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)