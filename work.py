
# This is the script run by player 2. 
# It allows the user to join a game by connecting to 
# the designated port that player 1 is listening on 

import sys

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from connection import CommandConnFactory
from game_state import GameState

class Joiner:
	def __init__(self, screen, address, port):
		self.screen = screen
		self.address = address
		self.port = port

	def start(self):
		#Initialize GameState
		gs = GameState(self.screen,2)

		#Create Looping Call
		lc = LoopingCall(gs.gameLoop)
		lc.start(.0166666666)

		#Begin Connecting
		reactor.connectTCP(self.address,self.port,CommandConnFactory(gs,False))

if __name__ == '__main__':	
	sys.exit('trying running memory.py')

