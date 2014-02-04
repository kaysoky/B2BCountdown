import pygame
import sys
import math

from elem_SSVEPRect import elem_SSVEPRect  
from elem_CompassPair import elem_CompassPair  
from elem_Generic import elem_Generic
from elem_Indicators import elem_Indicators

#This class represents a single set of stuff to display on the screen.  That includes all titles, stimuli, compasses, feedback, and video output.

class StimScreen():
	#Fields:
	#showFPS - true if frames per second is to be displayed, false otherwise
	#showFeedback - true if feedback indicators are to be displayed.  They will automatically appear under each rectangle element
	#screen - the pygame screen to which this screen will be drawn
	#elements - all rectangle/SSVEP elements
	#elementFreqs - the flicker frequency of each rectangle/SSVEP element
	#elementUpdateTime - how long it has been since the resctangle/SSVEP element was last drawn to the screen
	#feedbackState - the state that determines what color to draw the feedback indicators.  1 if red, 2 if yellow, black otherwise.
	#generics - surfaces to which we can paint video, pictures, or just display text like titles and questions
	#genericUpdate - indicates if the surface has been updated and therefore needs to be drawn to the screen
	#compassElements - elements to indicate direction (ie of the robot)
	#compassUpdated - indicates if the compass element has been updated and therefore needs to be drawn to the screen
	#clock - used for keeping track of time and FPS


	#Constants:
	FEEDBACK_SIZE = (130,17)
	BACK_COLOR = pygame.color.Color('#CCAA88')
	FPS_COLOR = None
	
	GENERIC=0
	SSVEP_RECT=1
	
	#Initialize a new StimScreen
	#params:
	#screen - the pygame screen to which this StimScreen will be drawn
	def __init__ (self,screen):

		# Start a clock for tracking stimulus color flips.
		self.clock=pygame.time.Clock()
		self.elements = []
		self.screen = screen

		self.FPS_COLOR = self.invertColor(self.BACK_COLOR)

		self.showFPS = True
		self.showFeedback = True
		self.elementFreqs = []
		self.elementUpdateTime = []
		self.feedbackState = []
		self.feedbackUpdated = []
		self.generics = []
		self.genericUpdated = []
		self.compassElements = []
		self.compassUpdated = []
		self.indicators = []
		self.renderBackground()

		
	#Adds a rectangular SSVEP/Rectangle flicker element to the screen
	#params:
	#x,y - the pixel location of the upper-left corner of the element, measured in pixels from the upper-left corner of the window
	#width,height - the pixel dimensions of the rectangle
	#color1,2 - the colors the element will alternate/flicker between. must be valid pygame.color color names
	#text - the text to display in the element
	#freq - the alternation/flicker frequency.
	def addRectangleElement(self,x,y,width,height,color1,color2,text,freq):
		self.elements.append(elem_SSVEPRect(x, y, width, height, color1, color2, text, self.screen))
		self.elementFreqs.append(freq)
		self.feedbackState.append(0)
		self.feedbackUpdated.append(True)
		self.updateIndicators=True
		self.elementUpdateTime.append(0)

	#Adds a new compass pair element
	#params:
	#x,y - the pixel location of the center of rotation the element, measured in pixels from the upper-left corner of the window
	#radius - the length of the compass arrows
	#initTheta1,2 - the starting heading of the compass heads in radians, 0 is east.
	#color1,2 - the color of the two arrows. must be valid pygame.color color names
	def addCompassPairElement(self,x,y,radius,initTheta1,initTheta2,color1,color2):
		self.compassElements.append(elem_CompassPair(x, y, radius, initTheta1, initTheta2, color1, color2, self.screen))
		self.compassUpdated.append(True)
		self.updateIndicators=True

	#Add a generic element that can be used to show pictures, video, or simply text.
	#params:
	#x,y - the pixel location of the upper-left corner of the element, measured in pixels from the upper-left corner of the window
	#width,height - the pixel dimensions of the element
	#picture - optional picture to display in the element
	#text - text to display on the element
	def addGeneric(self,x,y,width,height,picture,text):
		self.generics.append(elem_Generic(x,y,width,height,picture,text,self.BACK_COLOR,self.screen))
		self.genericUpdated.append(True)
		self.updateIndicators=True

	#Add a generic element that can be used to show pictures, video, or simply text.  Has a green background.
	#params:
	#x,y - the pixel location of the upper-left corner of the element, measured in pixels from the upper-left corner of the window
	#width,height - the pixel dimensions of the element
	#picture - optional picture to display in the element
	#text - text to display on the element
	def addGenericGreen(self,x,y,width,height,picture,text,fitted=False):
		newElem = elem_Generic(x,y,width,height,picture,text,pygame.color.Color('#CCDD66'),self.screen,fitted=fitted)
		newElem.font_size = 40
		self.generics.append(newElem)
		self.genericUpdated.append(True)
		self.updateIndicators=True
		
	#Add a generic element that can be used to show pictures, video, or simply text.  Has a green background and somewhat larger text.
	#params:
	#x,y - the pixel location of the upper-left corner of the element, measured in pixels from the upper-left corner of the window
	#width,height - the pixel dimensions of the element
	#picture - optional picture to display in the element
	#text - text to display on the element
	def addGenericBigGreen(self,x,y,width,height,picture,text):
		newElem = elem_Generic(x,y,width,height,picture,text,pygame.color.Color('#CCDD66'),self.screen)
		newElem.font_size = 72
		self.generics.append(newElem)
		self.genericUpdated.append(True)
		self.updateIndicators=True

	#Add a generic element that can be used to show pictures, video, or simply text.  Has a larger than normal text and green background.
	#params:
	#x,y - the pixel location of the upper-left corner of the element, measured in pixels from the upper-left corner of the window
	#width,height - the pixel dimensions of the element
	#picture - optional picture to display in the element
	#text - text to display on the element
	def addGenericBigText(self,x,y,width,height,picture,text):
		newElem = elem_Generic(x,y,width,height,picture,text,pygame.color.Color('#CCDD66'),self.screen)
		newElem.font_size = 75
		newElem.font_color = pygame.color.Color('#0000FF')
		self.generics.append(newElem)
		self.genericUpdated.append(True)
		self.updateIndicators=True
	
	#Add an indicator element to this screen
	#params:
	#color - the color of text to render
	def addIndicators(self,color):
		self.indicators.append(elem_Indicators(color,self.screen))
		self.updateIndicators=True
		
	
	#Add an indicator to an indicator element
	#params:
	#indicatorIndex - the index in self.indicators of the Indicators element to which we will add this indicator
	#text - the text of the indicator
	#x,y - the x,y location of the indicator on the screen
	def addIndicator(self,indicatorIndex,text,x,y):
		self.indicators[int(indicatorIndex)].addTextElement(str(text),x,y)
		
	#Clear all the indicators on a given text element
	#params:
	#indicatorIndex - the index in self.indicators of the Indicators element you want to clear
	def clearIndicator(self,indicatorIndex):
		self.indicators[int(indicatorIndex)].clearTextElements()

	#Change the angle of a compass pair
	#params:
	#compass - index in compassElements of the compass to rotate
	#arrow - which of the two arrows to rotate (either 0 or 1)
	#radians - magnitude of rotation in radians
	def changeCompassAngle(self,compass,arrow,radians):
		if(len(self.compassElements)>=compass):
			if(arrow==0):
				self.compassElements[compass].rotateArrow1(radians)
				self.compassUpdated[compass]=True
			elif(arrow==1):
				self.compassElements[compass].rotateArrow2(radians)
				self.compassUpdated[compass]=True

	#Sets the text of a rectangular/SSVEP element
	#params:
	#element - the index of elements[] of the element you want to change text for
	#text - the text to put on the element
	#elemType [OPTIONAL] - select the type of element you are indexing to write text to
	def setElementText(self,element,text,elemType=SSVEP_RECT):
		if(elemType==StimScreen.SSVEP_RECT):
			if(len(self.elements)>=element):
				self.elements[element].text=text
		elif(elemType==StimScreen.GENERIC):
			if(int(element) in range(len(self.generics))):
				self.generics[int(element)].text=text
				self.genericUpdated[int(element)]=True

		for i in range(len(self.feedbackUpdated)):
			self.feedbackUpdated[i]=True	

	#Sets the state of a given feedback indicator
	#params:
	#feedback - the index of the rectangular/SSVEP element to which this feedback corresponds
	#state - the state to set the feedback
	#	1 - Red
	#	2 - Yellow
	#	Else - Black
	def setFeedbackState(self,feedback,state):
		feedback = int(feedback)
		state = int(state)
		if(len(self.feedbackState)-1>=feedback):
			self.feedbackState[feedback] = state
			self.feedbackUpdated[feedback] = True
			self.updateIndicators=True

	#Changes the picture of the generic at genericIndex to the pygame surface given by 'surface'
	def pictureUpdate(self,surface,genericIndex):
		self.generics[genericIndex].changePicture(surface)
		self.genericUpdated[genericIndex]=True
		self.updateIndicators=True

	#Toggle the FPS display from on to off or vice-versa
	def toggleFPS(self):
		self.showFPS = not(self.showFPS)
	
	#Renders the entire background of the window
	def renderBackground(self):
		pygame.display.update(pygame.draw.rect(self.screen, self.BACK_COLOR, [0,0]+list(self.screen.get_size())))

	#Renders the background behind the text showing FPS
	def renderFPSBackground(self):
		font=pygame.font.Font(None,17)
		text2 = font.render('PPPPPPPPPP', True, self.BACK_COLOR, self.BACK_COLOR)
		textRect2 = text2.get_rect().inflate(2,4)
		pygame.display.update(pygame.draw.rect(self.screen,self.BACK_COLOR,textRect2))

	#Renders the text showing FPS
	def renderFPS(self):
		font=pygame.font.Font(None,17)
		textColor = self.FPS_COLOR
		textBGColor = self.BACK_COLOR
		time = self.clock.get_fps()
		if math.isinf(time):
			return
		text = font.render('FPS: '+str(int(self.clock.get_fps())), True, textColor, textBGColor)
		textRect = text.get_rect()
		textRect.centerx, textRect.centery = 30,10
		self.screen.blit(text,textRect)
		pygame.display.update(textRect)
	
	#Renders all compasses to the screen
	def renderCompasses(self):
		sWidth,sHeight = self.screen.get_size()
		for i in range(len(self.compassElements)):
			if(self.compassUpdated[i]):
				self.compassElements[i].draw()
				self.compassUpdated[i]=False

	#Render all indicator elements to the screen
	def renderIndicators(self):
		for i in range(len(self.indicators)):
			self.indicators[i].draw()
		self.updateIndicators=False
			
	
	#Renders all generic elements to the screen
	def renderGenerics(self):
		for i in range(len(self.generics)):
			if(self.genericUpdated[i]):
				self.generics[i].draw()
				self.genericUpdated[i]=False

	#Renders all feedback indicators
	def renderFeedbacks(self):
		for i in range(len(self.elements)):
			if(self.feedbackUpdated[i]):
				self.feedbackUpdated[i] = False
				if(self.feedbackState[i] == 1):
					color=pygame.color.Color('red')
				elif(self.feedbackState[i] == 2):
					color=pygame.color.Color('yellow')
				else:
					color=pygame.color.Color('black')
			
				feedX = self.elements[i].x + self.elements[i].width/2 - self.FEEDBACK_SIZE[0]/2
				feedY = self.elements[i].y + self.elements[i].height + self.FEEDBACK_SIZE[1]/3

				rect=pygame.draw.rect(self.screen, color, pygame.Rect(feedX,feedY,self.FEEDBACK_SIZE[0],self.FEEDBACK_SIZE[1]))
				pygame.display.update(rect)
	
	#Returns the inverted color of 'color'
	def invertColor(self,color):
		newR = 255-color.r
		newG = 255-color.g
		newB = 255-color.b
		newA = color.a
		return pygame.color.Color(newR,newG,newB,newA)

	#Renders this screen once
	def render(self):
		if(len(self.generics)>0):
			self.renderGenerics()

		if(self.showFPS):
			self.renderFPS()

		if(len(self.compassElements)>0):
			self.renderCompasses()
			
		if(len(self.indicators)>0):
			self.renderIndicators()

		self.clock.tick()
		if(len(self.elements)>0):
			for i in range(len(self.elements)):
				self.elementUpdateTime[i] += self.clock.get_time()
				if(self.elementUpdateTime[i] >= (1000/self.elementFreqs[i])):
					self.elements[i].flipColors()
					self.elements[i].draw()
					self.elementUpdateTime[i]= 0

		if(self.showFeedback):
			self.renderFeedbacks()

