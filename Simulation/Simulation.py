import sys, math, time
import numpy as np
from matplotlib import pyplot as plt

class coord:
  def __init__(self, x, y, z=0):
    self.x = x
    self.y = y
    self.z = z
  def __add__(self, coord2):
    return coord(self.x + coord2.x, self.y + coord2.y, self.z + coord2.z)
  def __sub__(self, coord2):
    return coord(self.x - coord2.x, self.y - coord2.y, self.z - coord2.z)
  def __mul__(self, constant):
    return coord(self.x * constant, self.y * constant, self.z * constant)
  def __iadd__(self, coord2):
    self.x += coord2.x
    self.y += coord2.y
    self.z += coord2.z
    return self
  def __isub__(self, coord2):
    self.x -= coord2.x
    self.y -= coord2.y
    self.z -= coord2.z
  def __neg__(self):
    self.x = -self.x
    self.y = -self.y
    self.z = -self.z
  def __eq__(self, coord2):
    if self.x == coord2.x and self.y == coord2.y and self.z == coord2.z:
      return True
    return False
  def __ne__(self, coord2):
    return not (self == coord2)
  def distance(self, coord2):
    return np.linalg.norm([self.x - coord2.x, self.y - coord2.y, self.z - coord2.z])

class Sensor:
  def __init__(self, sensorID, sensorType, trueLocation, distanceRange, neighbors=[], **kwargs):
    self.sensorID       = sensorID
    self.sensorType     = sensorType
    self.trueLocation   = trueLocation
    self.distanceRange  = distanceRange
    self.neighbors      = neighbors
    if self.sensorType == 'MOBILE':
      self.velocity     = kwargs['velocity']
      self.lblimit      = kwargs['lblimit']
      self.rtlimit      = kwargs['rtlimit']
      self.uncertainty  = kwargs['uncertainty']
    
  def locationUpdate(self, tick):
    if self.sensorType != 'MOBILE':
      raise TypeError('Location Update is not possible for immobile sensor')
    if self.trueLocation.x < self.lblimit.x:
      self.velocity.x   = abs(self.velocity.x)
    elif self.trueLocation.x > self.rtlimit.x:
      self.velocity.x   = -abs(self.velocity.x)
    if self.trueLocation.y < self.lblimit.y:
      self.velocity.y   = abs(self.velocity.y)
    elif self.trueLocation.y > self.rtlimit.y:
      self.velocity.y   = -abs(self.velocity.y)
    self.trueLocation += self.velocity*tick
    
  def neighborsUpdate(self, anchors, tags):
    self.neighbors = {}
    for anchor in anchors:
      if self.trueLocation.distance(anchor.trueLocation) < self.distanceRange:
        self.neighbors[anchor.sensorID] = self.distance(anchor)
    if tagLinks:
      for tag in tags:
        if self.trueLocation.distance(tag.trueLocation) < self.distanceRange and self.sensorID != tag.sensorID:
          self.neighbors[tag.sensorID] = self.distance(tag)
  
  def uncertaintyUpdate(self):
    length = len(self.neighbors)
    if length <= 2:
      self.uncertainty *= 1.02
    elif length == 3:
      self.uncertainty *= 1.002
    else:
      self.uncertainty /= (1.02**(length-3))
  
  def distance(self, sensor2):
    return self.trueLocation.distance(sensor2.trueLocation)

Anchors         = []
numAnchors      = 6
anchorLocations = [coord(0.2,0.2), coord(4,0.2), coord(3,9.8), coord(9.8,6), coord(9.8,9.8), coord(0.2,5)]
anchorPoints    = ['rx', 'bx', 'gx', 'mx', 'kx', 'yx', 'cx']

Tags            = []
numTags         = 3
tagLocations    = [coord(1,2), coord(5,5), coord(9,1)]
tagVelocities   = [coord(0.2,0.5), coord(-0.3,0.4), coord(0.1,0.7)]
tagLBLimits     = [coord(1,1), coord(7,6), coord(3,0.5)]
tagRTLimits     = [coord(5,7), coord(10,9), coord(9.5,5.5)]
tagPoints       = ['ro', 'go', 'bo']
tagLines        = ['r-', 'g-', 'b-']

tick            =     1
tagLinks        =  True
finalTime       =   800
sensingRadius   =     7

for i in range(numAnchors):
  Anchors.append(Sensor('A'+str(i), 'FIXED',  anchorLocations[i], sensingRadius))
for i in range(numTags):
  Tags.append   (Sensor('T'+str(i), 'MOBILE', tagLocations[i],    sensingRadius, velocity = tagVelocities[i], lblimit = tagLBLimits[i], rtlimit = tagRTLimits[i], uncertainty = 70))

for t in range(numTags):
  Tags[i].neighborsUpdate(Anchors, Tags)

frames = []
fig    = plt.figure()
plt.get_current_fig_manager().window.state('zoomed')
plt.get_current_fig_manager().window.attributes('-fullscreen', True)
ax     = fig.add_subplot(111)
fig.show()
for t in np.arange(0, finalTime, tick):
  ax.clear()
  plt.xlim(0,10)
  plt.ylim(0,10)
  
  for i in range(numAnchors):
    ax.plot(Anchors[i].trueLocation.x, Anchors[i].trueLocation.y, anchorPoints[i])
  for i in range(numTags):
    Tags[i].locationUpdate(tick)
  
  for i in range(numTags):
    Tags[i].neighborsUpdate(Anchors, Tags)
    Tags[i].uncertaintyUpdate()
    loc1 = Tags[i].trueLocation
    ax.plot(loc1.x, loc1.y, tagPoints[i], markersize = Tags[i].uncertainty)
    for neighbor in Tags[i].neighbors.keys():
      if neighbor[0] == 'A':
        loc2 = [anchor.trueLocation for anchor in Anchors if anchor.sensorID == neighbor][0]
        ax.plot([loc1.x, loc2.x],[loc1.y, loc2.y], tagLines[i])
      else:
        loc2 = [tag.trueLocation for tag in Tags if tag.sensorID == neighbor][0]
        ax.plot([loc1.x, loc2.x],[loc1.y, loc2.y], 'y-')
  fig.canvas.draw()