
# This is the script run by player 1. 
# It allows the user to host a game by listening on 
# the designated port until player 2 joins 

import sys

from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

from connection import CommandConnFactory
from game_state import GameState

class Hoster:
	def __init__(self, screen, port):
		self.screen = screen
		self.port = port

	def start(self):
		# Set up the connection between the state and the network
		inqueue = DeferredQueue()
		outqueue = DeferredQueue()

		#Initialize GameState
		gs = GameState(self.screen,1,inqueue,outqueue)

		#Create Looping Call
		lc = LoopingCall(gs.gameLoop)
		lc.start(.0166666666)
		
		#Begin Listening
		connfactory = CommandConnFactory(inqueue,outqueue)
		reactor.listenTCP(self.port,connfactory)

if __name__ == '__main__':
	sys.exit('try running memory.py')

