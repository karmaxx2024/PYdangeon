import pygame
import random
from setting import *

TILE_WALL = 0 
TILE_FLOOR = 1
TILE_DOOR = 2
TILE_STAIRS = 3
TILE_TRAP = 4

class Room: 
  
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  def center(self):
    self.x2 = x + w
    self.y2 = y + h

  def interpects(self, other):
    return(
      self.x <= other.x2 + 1 and 
      self.x2 >= other.x - 1 and 
      self.y <= other.y2 + 1 and
      self.y2 >= other.y - 1 
    )

  def random_floor_point(self):
    rx = random.randint(self.x + 1, self.x2 - 2)
    ry = random.randint(self.y + 1, self.y2 - 2)
    return rx, ry






