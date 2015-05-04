from twisted.internet.protocol import ClientFactory, Factory
from twisted.protocols.basic import LineReceiver

from card import Card
from values import Values

#
# Class that sends and receives data
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

	def lineReceived(self, line):
		print 'line received: ' + line
		self.factory.inqueue.put(line)

	def sendMessage(self, msg):
		print 'line sent: ' + msg
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

