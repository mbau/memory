#run by the host

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
		# Set up the connection between the state and the network;
		# using queues gives a degree of seperation between the
		# communication and game logic, and making them be deferred
		# keeps it all asynchronous.
		inqueue = DeferredQueue()
		outqueue = DeferredQueue()

		#Initialize GameState
		gs = GameState(self,self.screen,1,inqueue,outqueue)

		#Create Looping Call
		self.lc = LoopingCall(gs.gameLoop)
		self.lc.start(.0166666666)
		
		#Begin Listening
		connfactory = CommandConnFactory(inqueue,outqueue)
		self.listening = reactor.listenTCP(self.port,connfactory)

	def stop(self, nextscreen=None):
		# Stop the GameState logic, and let go of the port on which we're listening
		self.lc.stop()
		self.listening.stopListening()

		# Start up the next screen, if there is one
		if nextscreen:
			nextscreen.start()
		else: reactor.stop()

if __name__ == '__main__':
	sys.exit('try running memory.py')

