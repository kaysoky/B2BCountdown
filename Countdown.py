import pygame
import math
import sys
import time
import random
import thread
import argparse
import datetime

from TCPIPWrapper import TCPServer, TCPClient
from pygame.locals import *
from GameScreen import GameScreen



pygame.init()


GUN_BASE_X = 392
GUN_BASE_Y = 658
GUN_LEN = 65
GUN_WIDTH = 20
GUN_SURFACE_SIZE = 32
MISSILE_DISTANCE = 550
MISSILE_INIT_PHASE = 0
AIRPLANE_INIT_PHASE = -0.555
END_PHASE = -2.4
MISSILE_LEN = 55
MISSILE_WIDTH = 32
FRAME_RATE = 30
MISSILE_AIR_TIME = 20
EXPLOSION_WIDTH = 250
EXPLOSION_HEIGHT = 250
AIRPLANE_WIDTH = 91
AIRPLANE_HEIGHT = 71
AIRPLANE_ALTITUDE = 150	#measured in pixel distance from the top of the screen
COUNTDOWN_FROM = 3 

TRIAL_START_PACKET = "t_start"
TRIAL_END_PACKET = "t_stop"


TMS_TRIGGER_SOUND = "fire.wav"


#used to mark the current trial and airplane or a missile
MODE_MISSILE = 0
MODE_AIRPLANE = 1


backImage = "Backdrop.bmp"
missileImage = "Missile.bmp"
explosionImage = "Explosion.png"
windowImage = "Window.png"
airplaneImage = "Airplane.png"
background = pygame.image.load(backImage)
missileImage = pygame.image.load(missileImage)
explosionImage = pygame.image.load(explosionImage)
windowImage = pygame.image.load(windowImage)
airplaneImage = pygame.image.load(airplaneImage)
pyScreen = pygame.display.set_mode(background.get_size())

SCREEN_WIDTH =  background.get_size()[0]
SCREEN_HEIGHT =  background.get_size()[1]

#returns a vector the same length as the vector given by [x,y], but rotated theta radians.  Offsets add an arbitrary amount to the X and Y coordinates.
def rotateVector(x,y,theta,offsetX,offsetY):
	reorientedX = x * math.cos(theta) - y * math.sin(theta)
	reorientedY = x * math.sin(theta) + y * math.cos(theta)

#	len = math.sqrt(math.pow(reorientedX,2) + math.pow(reorientedY,2))
#	orglen = math.sqrt(math.pow(x,2) + math.pow(y,2))

	return (reorientedX + offsetX , reorientedY + offsetY)

#give rectangle coordinates centered at 0,0 with orientation relative to positive x axis
def rectCoords(x,y,w,h,orientation):
	toReturn = [rotateVector(w/2,h/2.0,orientation,x,y),rotateVector(w/2,-h/2.0,orientation,x,y),rotateVector(-w/2,-h/2.0,orientation,x,y),rotateVector(-w/2,h/2.0,orientation,x,y)]

	return toReturn

#rect coordinates of the location magnitude and theta polar displacement from (offsetX,offsetY)
#theta in radians
def polarToRect(magnitude,theta,offsetX,offsetY):
	return (math.cos(theta) * magnitude  + offsetX, math.sin(theta) * magnitude + offsetY)



#blit transparent pixels across surface
def blankenize(surface):
	size = surface.get_size()
	w = size[0]
	h = size[1]
	pygame.draw.rect(surface, pygame.color.Color(0,0,0,0), pygame.Rect(0,0,w,h))

#returns missile surface and location  at angle 'phase' (measured in radians) from the positive x axis at distance 'distance' from the turret.
def placeMissile(phase,distance):
	surface = pygame.Surface((MISSILE_WIDTH,MISSILE_LEN),flags=pygame.SRCALPHA)
	surface.blit(missileImage,(0,0))
	surface = pygame.transform.rotate(surface,math.degrees(-phase))

	missileLoc = polarToRect(distance,phase,GUN_BASE_X,GUN_BASE_Y)

	return surface,missileLoc

#same as placeMissile, but does not revolve around the turret and rotate.  Takes a straight line across the screen.
#phase (radians) is angle between a ray drawn from the turret to the plane and the positive x-axis.
def placeAirplane(phase):
	surface = pygame.Surface((AIRPLANE_WIDTH,AIRPLANE_HEIGHT),flags=pygame.SRCALPHA)
	surface.blit(airplaneImage,(0,0))

	###calculate distance from turret to airplane s.t. it maintains constant height

	#sides of the triangle formed by turret, airplane, and drawing lines from them
	#	parallel to the x and y axes
	displacement_v = GUN_BASE_Y - AIRPLANE_ALTITUDE
	distance = displacement_v / math.sin(-phase) 

	displacement_h = math.sqrt(math.pow(distance,2) - math.pow(displacement_v,2))

	if phase < -math.pi/2:
		displacement_h *= -1

	airplaneLoc = (displacement_h + GUN_BASE_X, AIRPLANE_ALTITUDE)

	return surface,airplaneLoc
	

#print a log message to the console with time stamp 
def log(msg):
	print str(datetime.datetime.now()) + ": " + msg


################
## Game Loops ##
################

if __name__ != "__main__":
    print "Unknown run configuration"
    exit()

parser = argparse.ArgumentParser()
parser.add_argument('--bci', nargs='+', help="IP and port of the BCI machine.  Just specify port to make a server connection", required=True)
parser.add_argument('--tms', nargs='+', help="IP and port of the TMS machine.  Just specify port to make a server connection", required=True)
args = parser.parse_args()

#network sockets
bciSocket = TCPServer(int(args.bci[0])) if len(args.bci) == 1 else TCPClient(args.bci[0], int(args.bci[1]))
tmsSocket = TCPServer(int(args.tms[0])) if len(args.tms) == 1 else TCPClient(args.tms[0], int(args.tms[1]))

x = GameScreen(pyScreen,backImage,pygame.color.Color(121,74,0,0))
#x.addTextElem("fps","FPS: ",1069,33,pygame.color.Color(255,229,187,255),pygame.color.Color(121,74,0,0),17)
x.addTextElem("score","Score: ",1164,55,pygame.color.Color(255,229,187,255),pygame.color.Color(121,74,0,0),36)
x.addTextElem("attempts","Attempts: ",1164,110,pygame.color.Color(255,229,187,255),pygame.color.Color(121,74,0,0),36)
x.addTextElem("bigAnyKey","Press space to play",646,407,pygame.color.Color(255,235,175,255),pygame.color.Color(121,74,0,0),72)
x.addTextElem("bigScore","Score: ",646,387,pygame.color.Color(255,235,175,255),pygame.color.Color(121,74,0,0),72)
x.addTextElem("bigAttempts","Attempts: ",646,487,pygame.color.Color(255,235,175,255),pygame.color.Color(121,74,0,0),72)
x.addTextElem("countdown","0",646,407,pygame.color.Color(255,235,175,255),pygame.color.Color(121,74,0,0),100)

clock=pygame.time.Clock()

goodScore = 0
badScore = 0
attempts = 0
gunOrientation = 0
phase = 0
gunColor =  pygame.color.Color(155,229,187,255)
reset = False
timeToQuit = False

gun = pygame.Surface((GUN_SURFACE_SIZE*2,GUN_SURFACE_SIZE*2),flags=pygame.SRCALPHA)
explosion = pygame.Surface((EXPLOSION_WIDTH,EXPLOSION_HEIGHT),flags=pygame.SRCALPHA)
explosion.blit(explosionImage,(0,0))
windowSize = background.get_size()
window = pygame.Surface((windowSize[0],windowSize[1]),flags = pygame.SRCALPHA)
window.blit(windowImage,(0,0))


#loop for splash screen
x.renderBackground()
x.renderElement(window,0,0)
x.renderText("bigAnyKey")
x.updateScreen()

while (not reset):
	clock.tick(FRAME_RATE)

	for event in pygame.event.get():
		if (event.type == pygame.KEYDOWN):
			if (event.key == pygame.K_SPACE):
				reset = True
			elif (event.key == pygame.K_q):
				exit()

reset = False
countdown = True


log("Starting experiment")

#### loop for the game ####
while (not timeToQuit):
	clock.tick(FRAME_RATE)

#	time = clock.get_fps()
#	if not math.isinf(time):
#		x.updateText("fps","FPS: " + str(round(time,0)))

	## count down to trial start ##	
	if countdown:
		i = COUNTDOWN_FROM
		x.renderBackground()

		while i>0:
			x.renderElement(window,0,0)
			x.updateText("countdown",str(i))
			x.renderText("countdown")
			x.updateScreen()
			clock.tick(1)
			i -= 1
		countdown = False
		for event in pygame.event.get():
			pass
		
	
		if random.randint(0,1) < 1:
			trialMode = MODE_MISSILE
			phase = MISSILE_INIT_PHASE
		else:
			trialMode = MODE_AIRPLANE
			phase = AIRPLANE_INIT_PHASE
			targetSurface,targetLoc = placeAirplane(phase)

		#purge any stuff in the socket stream
		qqq = bciSocket.recvmostrecent()
		
		#send trial start signal to the BCI to turn it on
		bciSocket.send(TRIAL_START_PACKET)

		#write out trial info to log		
		log("Starting trial: " + ("Missile" if trialMode == MODE_MISSILE else "Airplane"))
	x.updateText("score","Score: " + str(goodScore-badScore))
	x.updateText("attempts","Attempts: " + str(attempts))


	blankenize(gun)
	pygame.draw.polygon(gun,gunColor,rectCoords(GUN_SURFACE_SIZE,GUN_SURFACE_SIZE,GUN_LEN,GUN_WIDTH,gunOrientation))
	gunLoc = polarToRect(GUN_SURFACE_SIZE,gunOrientation,GUN_BASE_X,GUN_BASE_Y)
	

	if trialMode == MODE_MISSILE:
		targetSurface,targetLoc = placeMissile(phase,MISSILE_DISTANCE)
	else:
		targetSurface,targetLoc = placeAirplane(phase)
	

	x.renderBackground()
	x.renderElement(gun,gunLoc[0],gunLoc[1])
	x.renderElement(targetSurface,targetLoc[0],targetLoc[1])
#	x.renderText("fps")
	x.renderText("score")
	x.renderText("attempts")
	x.updateScreen()

	for event in pygame.event.get():
		if (event.type == pygame.KEYDOWN):
			if event.key==pygame.K_q:
					timeToQuit = True
			if event.key == pygame.K_a:
				print log("arming stimulator by key press")
				tmsSocket.send("3")
			if event.key == pygame.K_d:
				print log("disarming stimulator by key press")
				tmsSocket.send("4")
			if event.key == pygame.K_t:
				print log("triggering stimulator by key press")
				tmsSocket.send("1")
			if event.key == pygame.K_SPACE:
				x.renderElement(explosion,targetLoc[0]-EXPLOSION_WIDTH/2,targetLoc[1]-EXPLOSION_HEIGHT/2)
				rect = explosion.get_rect()
				rect.centerx, rect.centery = targetLoc[0], targetLoc[1]
				x.updateRect(rect)
				clock.tick(1)
				clock.tick(1)
				reset = True
				countdown = True
				
				log("Shot fired")
		
				if trialMode == MODE_MISSILE:
					goodScore += 1
				else:
					badScore += 1

	bciCommand = bciSocket.recvmostrecent()
	if not bciCommand=="":
		log("BCI input received.  Sending TMS pulse.")
		tmsSocket.send("1")
		#pygame.mixer.Sound(TMS_TRIGGER_SOUND).play()		


	if reset or phase<END_PHASE:
		attempts += 1
		countdown = True
		reset = False

		bciSocket.send(TRIAL_END_PACKET)

	
		log("Missiles hit: " + str(goodScore) + ", Airplanes hit: " + str(badScore) + ", Attempts: " + str(attempts))

	else:
		phase += END_PHASE/(FRAME_RATE*MISSILE_AIR_TIME)


	gunOrientation = phase



#loop for outro screen
x.renderBackground()
x.renderElement(window,0,0)
x.updateText("bigScore","Score: " + str(goodScore - badScore))
x.updateText("bigAttempts","Attempts: " + str(attempts))
x.renderText("bigScore")
x.renderText("bigAttempts")
x.updateScreen()
reset = False

while (not reset):
	clock.tick(FRAME_RATE)

	for event in pygame.event.get():
		if (event.type == pygame.KEYDOWN):
			reset = True



#print score to stdout
print "Missiles hit: " + str(goodScore)
print "Planes hit: " + str(badScore)
print "Attempts: " + str(attempts)


