
# This is the script run by player 2. 
# It allows the user to join a game by connecting to 
# the designated port that player 1 is listening on 

import sys

from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

from connection import CommandConnFactory
from game_state import GameState

class Joiner:
	def __init__(self, screen, address, port):
		self.screen = screen
		self.address = address
		self.port = port

	def start(self):
		# Set up the connection between the state and the network
		inqueue = DeferredQueue()
		outqueue = DeferredQueue()

		#Initialize GameState
		gs = GameState(self,self.screen,2,inqueue,outqueue)

		#Create Looping Call
		self.lc = LoopingCall(gs.gameLoop)
		self.lc.start(.0166666666)

		#Begin Connecting
		connfactory = CommandConnFactory(inqueue,outqueue)
		reactor.connectTCP(self.address,self.port,connfactory)

	def stop(self, nextscreen=None):
		self.lc.stop()

		if nextscreen:
			nextscreen.start()
		else: reactor.stop()

if __name__ == '__main__':	
	sys.exit('trying running memory.py')

