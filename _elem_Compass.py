import pygame
import numpy
import math


#Compass element that displays an arrow.

class elem_Compass():
	#Fields:
	#X,Y - integers representing position around which the arrow rotates
	#radius - length of the arrow
	#theta - the heading of the compass arrow in radians.  East is 0. North is pi/2, etc.
	#color - the color of the arrow


	#Constants:
	#_WH_RATIO - the ratio of the arrow's height to its width
	_WH_RATIO = 3.5


	#Params:
	#X,Y - integers representing position around which the arrow rotates
	#radius - length of the arrow
	#initTheta - the initial heading of the compass arrow in radians
	#color - the initial color of the arrow
	#screen - the pygame screen to which this compass will be drawn
	def __init__(self, x, y, radius, initTheta, color, screen):
		self.on = True
		self.x = x
		self.y = y
		self.radius = radius
		self.theta = initTheta
		self.color = color
		self.screen=screen

	#Params:
	#degrees - number of radians to rotate counter-clockwise
	def rotate(self,radians):
		self.theta += radians

	#renders the compass arrow to self.screen
	def draw(self):
		#vectors representing the start point of the drawing, the displacement from that point to the top/end point of the triangle, and a displacement from the start point to one of the corners of the triangle
		startPoint = numpy.array((self.x, self.y))
		vDisplace = numpy.array((self.radius * math.cos(self.theta), self.radius * math.sin(self.theta)))	
		hDisplace = numpy.array((self.radius/self._WH_RATIO * math.cos(self.theta-math.pi/2), self.radius/self._WH_RATIO * math.sin(self.theta-math.pi/2)))

		#three points representing the triangle
		arrowPoints = (startPoint+vDisplace, startPoint+hDisplace, startPoint-hDisplace)

		#draw the triangle
		pygame.display.update(pygame.draw.polygon(self.screen, self.color, arrowPoints))	
	
