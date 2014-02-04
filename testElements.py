import numpy
import pygame
import math
import sys
from multiprocessing import Process,Manager,Queue
import time
import random

sys.path.append("/home/mmattb/HBCI/HBCI/codes/MenuStimuli/ModularPythonStimuli/SSVEP/layouts")


from pygame.locals import *
from StimScreen import StimScreen
from StimSystem import StimSystem


qIn = Queue()
qOut = Queue()


def run(qIn,qOut):
	x = StimSystem("Hairy Octopus",(1280,1024),qIn,qOut)
	x.addMenu("layout_test")
	x.run(0)

def getIn(qIn,qOut):
	done = False
	while not done:
		if(qIn.qsize()>0):
			s = qIn.get()
			if(s == pygame.K_q):
				done = True
				qOut.put(("quit",))
			if(s == pygame.K_a):
				x,y = random.uniform(0,1280),random.uniform(0,1024)
				qOut.put(("indicate",0,"x",x,y))


pr = (Process(target=getIn,args=(qIn,qOut)),Process(target=run,args=(qOut,qIn)))

for p in pr:
	p.start()

