from twisted.internet.protocol import ClientFactory, Factory
from twisted.protocols.basic import LineReceiver

from card import Card

#
# Class that sends and receives data; this is very lightweight, since it was
# decided that seperation of concerns would be best served by keeping all of
# the game logic seperate from the communication logic. This is essentially
# just a relayer used to hook up some DeferredQueues to and from the real code
# (one half of which is Twisted, the other our game logic.
#
class CommandConn(LineReceiver):
	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		print 'command connection made'
		self.factory.inqueue.put('connection_made')

		self.factory.outqueue.get().addCallback(self.sendMessage)

	def connectionLost(self, reason):
		print 'command connection lost: ' + reason.getErrorMessage()

	# Take any received messages and put them into a DeferredQueue for
	# other code to handle.
	def lineReceived(self, line):
#		print 'line received: ' + line
		self.factory.inqueue.put(line)

	# Using a DeferredQueue, relay messages out across the network
	def sendMessage(self, msg):
#		print 'line sent: ' + msg
		self.sendLine(msg)

		self.factory.outqueue.get().addCallback(self.sendMessage)

#
# Creates CommandConn Protocol
#
class CommandConnFactory(ClientFactory, Factory):
	def __init__(self, inqueue, outqueue):
		self.inqueue = inqueue
		self.outqueue = outqueue

	def buildProtocol(self, addr):
		return CommandConn(self)

