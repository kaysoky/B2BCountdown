import TCPIPWrapper
import pygame
s = TCPIPWrapper.TCPServer(2222)
clock = pygame.time.Clock()
while True:
	clock.tick(10)
	print s.recvmostrecent()
