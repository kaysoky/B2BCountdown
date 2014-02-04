import pygame
import sys
import math


class GameScreen():

	
	#Initialize a new StimScreen
	#params:
	#screen - the pygame screen to which this StimScreen will be drawn
        #backImage - string of path to background image (does this do relative?)
        #textColor - color of text printed on screen
	def __init__ (self,screen,backImage,textColor):
		pygame.init()

		# Start a clock for tracking stimulus color flips.
		self.clock=pygame.time.Clock()
		self.screen = screen

		self.background = pygame.image.load(backImage)
		self.backgroundSize = self.background.get_size()
		self.screen = pygame.display.set_mode(self.backgroundSize)

		self.textColor = textColor

		self.textElems = {}

	#Returns the inverted color of 'color'
	def invertColor(self,color):
		newR = 255-color.r
		newG = 255-color.g
		newB = 255-color.b
		newA = color.a
		return pygame.color.Color(newR,newG,newB,newA)

	def addTextElem(self,elemName,text,x,y,backColor,textColor,size):
		self.textElems[elemName] = (text,x,y,backColor,textColor,size)

	def updateText(self,elemName,text):
		old = self.textElems[elemName]
		self.textElems[elemName] = (text,old[1],old[2],old[3],old[4],old[5])

	def renderElement(self,element,x,y):
		self.screen.blit(element,(x,y))
		size = element.get_size()
	
	def renderBackground(self):
		self.screen.blit(self.background, (0,0))
	
	def renderText(self,elemName):

		elem = self.textElems[elemName]

		font=pygame.font.Font(None,elem[5])
		textColor = elem[4]
		textBGColor = elem[3]
		text = elem[0]
		x = elem[1]
		y = elem[2]
		
		renderedText = font.render(text, True, textColor, textBGColor)
		textRect = renderedText.get_rect()
		textRect.centerx, textRect.centery = x,y
		self.screen.blit(renderedText,textRect)


	def updateScreen(self):
		pygame.display.update(pygame.Rect(0, 0, self.backgroundSize[0], self.backgroundSize[1]))

	def updateRect(self,rect):
		pygame.display.update(rect)

