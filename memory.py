#!/usr/bin/python

# This desplays the menu for the game
# Memory and gives the user a choice to either host
# a game, join a game or quit the game


import pygame

from main_screen import MainScreen
from twisted.internet import reactor

if __name__ == '__main__':
	# General setup
	pygame.init()
	pygame.key.set_repeat(500,30)

	# Define constants
	size = 970, 800

	# Create screen
	screen = pygame.display.set_mode(size)

	# Start up the program
	MainScreen(screen).start()

	reactor.run()

