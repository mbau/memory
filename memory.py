#!/usr/bin/python

# This desplays the menu for the game
# Memory and gives the user a choice to either host
# a game, join a game or quit the game


import pygame
import dumbmenu as dm
import os
import sys

from work import Joiner
from home import Hoster

pygame.init()

#Define Colors
red   = 255,  0,  0
green =   0,255,  0
gold  = 255,215,  0  
blue  =   0,  0,255
black =   0,  0,  0

# Process command-line arguments
if len(sys.argv) > 1:
	try:
		address = sys.argv[1]
		port = int(sys.argv[2])
	except IndexError:
		sys.exit('usage: ' + sys.argv[0] + ' server-address server-port')
else:
	address = 'localhost'
	port = 40100

	print 'using default server settings: ' + address + ' ' + str(port)

#create screen
size = width, height = 970,800	
screen = pygame.display.set_mode(size)
screen.fill(black)

backg = pygame.image.load('WALLP2.png')
screen.blit(backg, (0,0))

pygame.display.update()
pygame.key.set_repeat(500,30)

#Set options
choose = dm.dumbmenu(screen, [
                        'Host Game',
                        'Join Game',
                        'Quit Game'], 385,300,None,50,1.4,gold,red)

if choose == 0: # Host the game
	Hoster(screen,port).start()
elif choose == 1: # Join the game
	Joiner(screen,address,port).start()
elif choose == 2: # Exit the game
	pass

