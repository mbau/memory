import pickle

from twisted.internet.protocol import ClientFactory, Factory, Protocol

from card import Card
from values import Values

#
# Class that sends and receives data
#
class CommandConn(Protocol):
	def __init__(self, gs, ishost):
		self.gs = gs #save gamespace
		self.gs.command = self #Save this connection in gamespace
		self.ishost = ishost
		self.values = Values()
		self.first = 0

	def connectionMade(self):
		print "Command Connection Established."

		if self.ishost:
			self.gs.start = True #Show game board
			self.send() #Send initial game space state

	def send(self):
		print "Send"
		self.values.save(self.gs)
		pd = pickle.dumps(self.values)
		self.transport.write(pd)

	def dataReceived(self, data):
		print "Receive"
		self.data = pickle.loads(data)

		if not self.ishost and self.first == 0:
			#Receives initial gamespace
			self.first+=1
			self.loadFirst()
		else:
			self.load()

		self.gs.gameLoop() #Update game board

	def loadFirst(self):
		#Loads all data received from connection
		self.gs.firstCard = self.data.firstCard
		self.gs.message = self.data.message
		self.gs.p1 = self.data.p1
		self.gs.p2 = self.data.p2
		self.gs.turn = self.data.turn
		self.gs.timer = self.data.timer
		self.gs.startTimer = self.data.startTimer

		#Because first load, re-initialize cards
		self.gs.card_list = dict()
		width = -150
		height = 80
		for i in range(0,24):
			if i % 4 == 0:
				width = width + 160
				height = 100
			self.gs.card_list[i] = Card(self,width,height,self.data.card_value[i])
			height = height + 160


		for i in range(0,24):
			self.gs.card_list[i].curFrame = self.data.card_curFrame[i]
			self.gs.card_list[i].Flip = self.data.card_Flip[i]
			self.gs.card_list[i].flipDirection = self.data.card_flipDirection[i]
			self.gs.card_list[i].selected = self.data.card_selected[i]
			self.gs.card_list[i].matched = self.data.card_matched[i]
			self.gs.card_list[i].value = self.data.card_value[i]

	def load(self):
		#Loads all data received from connection
		self.gs.firstCard = self.data.firstCard
		self.gs.message = self.data.message
		self.gs.p1 = self.data.p1
		self.gs.p2 = self.data.p2
		self.gs.turn = self.data.turn
		self.gs.timer = self.data.timer
		self.gs.startTimer = self.data.startTimer

		for i in range(0,24):
			self.gs.card_list[i].curFrame = self.data.card_curFrame[i]
			self.gs.card_list[i].Flip = self.data.card_Flip[i]
			self.gs.card_list[i].flipDirection = self.data.card_flipDirection[i]
			self.gs.card_list[i].selected = self.data.card_selected[i]
			self.gs.card_list[i].matched = self.data.card_matched[i]
			self.gs.card_list[i].value = self.data.card_value[i]

#
# Creates CommandConn Protocol
#
class CommandConnFactory(ClientFactory, Factory):
	def __init__(self, gs, ishost):
		self.gs = gs
		self.ishost = ishost

	def buildProtocol(self, addr):
		return CommandConn(self.gs,self.ishost)

	def clientConnectionLost(self, connector, reason):
		print 'Lost connection.  Reason:', reason

	def clientConnectionFailed(self, connector, reason):
		print 'Connection failed. Reason:', reason

