
# This is the script run by player 2. 
# It allows the user to join a game by connecting to 
# the designated port that player 1 is listening on 

import math
import pygame
import os, sys
from pygame.locals import *
import random
from twisted.internet import protocol, reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.protocol import Protocol, ClientFactory
import pickle
from twisted.internet.task import LoopingCall

from card import Card
from values import Values

#
# Class that stores game board state
#
class GameSpace:
	def __init__(self, screen):
		self.screen = screen

		self.size = self.width, self.height = self.screen.get_size()
		self.black = 0, 0, 0

	def main(self):
		#Basic Initializations
		self.firstCard = 0 #Stores number of cards that have been selected
		self.message = "P1 turn" #Whose turn is it?
		self.p1 = 0 #Score
		self.p2 = 0 #Score
		self.turn = 1 # If > 0, then P1 turn. If < 0, then P2 turn
		self.command = None #Stores the CommandConn class
		self.timer = 0 #Used to track time after 2 cards are selected
		self.startTimer = False #True when time is on
		self.GameOver = False

		self.initializeCards()


	def initializeCards(self):

		#initialize card dictionary which will be used to insure
		#that only 2 of each image is placed on board
		self.cards = dict()
		for i in range(0,12):
			self.cards[i] = 0

		#Initialize card_list dict which will contain 24 
		#instances of the class Card to represent the 
		#24 cards on the board
		self.card_list = dict()
		width = -150
		height = 80
		for i in range(0,24):
			if i % 4 == 0:
				width = width + 160
				height = 100
			
			self.card_list[i] = Card(self,width,height,self.getValue())			
			height = height + 160


	def getValue(self):
		#Returns the value of the card and insures that 
		#only 2 cards will have the same value
		x = 0
		y = 0
		while y == 0:
			x = random.randint(0,11)
			if(self.cards[x] < 2):
				self.cards[x]+=1
				y = 1
		return x


	def gameLoop(self):
		# handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				if self.command != None:
					self.command.transport.loseConnection()  
				pygame.quit()     				
				sys.exit()
			if event.type == MOUSEBUTTONDOWN and event.button == 1:
				#User clicks card and it is his/her turn
				if self.turn < 0:
					for i in self.card_list.keys():				
						if(self.card_list[i].rect.collidepoint(pygame.mouse.get_pos())):
							#As long as 2 cards have not already been selected, 
							#and the card clicked is not already matched or already selected, then flip it					
							if self.startTimer is not True and self.card_list[i].matched is False and self.card_list[i].selected is False:
								self.card_list[i].Flip = True
								self.card_list[i].selected = True
								self.firstCard+=1
				else:
					print "Not your turn"

		#If 2 cards have been selected, then start the timer
		if self.firstCard == 2:
			self.startTimer = True
		else:
			self.startTimer = False

		#If the timer is started, then increment timer
		if self.startTimer is True:
			self.timer+=1
		else:
			self.timer = 0

		
		#After 3 seconds, update score, switch turn and flip cards back over
		if self.timer > 180:
			for i in self.card_list.keys():
				for j in self.card_list.keys():
					#The 2 cards are a match
					if self.card_list[i].selected is True and self.card_list[j].selected is True and self.card_list[i].value == self.card_list[j].value and i != j:
						self.card_list[i].matched = True
						self.card_list[j].matched = True
						self.card_list[j].selected = False
						self.card_list[i].selected = False

						#Update score
						if self.turn > 0:
							self.p1+=1
						else:
							self.p2+=1

						self.firstCard = 0
						self.startTimer = False

					#The 2 cards are not a match
					if self.card_list[i].selected is True and self.card_list[j].selected is True and i != j:
						#Flip the cards back over
						self.card_list[i].Flip = True
						self.card_list[j].Flip = True
						self.card_list[j].selected = False
						self.card_list[i].selected = False
						self.firstCard = 0
						self.startTimer = False

			#Change turns
			self.turn*=-1
			if self.turn > 0:
				#Tell P1 it's their turn
				self.message = "P1 turn"
				self.command.send()
			else:
				self.message = "P2 turn"
					
							
											

		# send a tick to every game object!
		for i in self.card_list.keys():
			self.card_list[i].tick()

		#Set labels
		myfont = pygame.font.SysFont("monospace",30)
		self.label = myfont.render("Memory ",1,(250,215,0))
		self.turnlabel = myfont.render(str(self.message),1,(250,215,0))
		self.player1 = myfont.render("Player 1: "+str(self.p1),1,(250,215,0))
		self.player2 = myfont.render("Player 2: "+str(self.p2),1,(250,215,0))
		self.gameover = myfont.render("GAME OVER",3,(250,215,0))

		#Make screen black
		self.screen.fill(self.black)

		#display cards
		for i in self.card_list.keys():
			self.screen.blit(self.card_list[i].image,self.card_list[i].rect)

		#display labels
		self.screen.blit(self.label,(430,30))
		self.screen.blit(self.player1,(20,30))
		self.screen.blit(self.player2,(750,30))
		self.screen.blit(self.turnlabel,(430,750))

		#Check if game over
		self.GameOver = True
		for i in self.card_list.keys():
			if self.card_list[i].matched is False:
				self.GameOver = False

		#If game over, display words
		if self.GameOver is True:
			self.screen.blit(self.gameover,(400,400))

		pygame.display.flip()

		#If it is player 2 turn, then send hte game state to player 1
		if self.command != None and self.turn < 0:
			self.command.send()

#
# Class that sends and receives data
#
class CommandConn(Protocol):
	def __init__(self,gs=None):
		self.gs = gs #save gamespace
		self.gs.command = self #Save this connection in gamespace
		self.values = Values()
		self.first = 0 

	def connectionMade(self): 
		print "Command Connection Established."

	def send(self):
		print "Send"
		self.values.save(self.gs)
		pd = pickle.dumps(self.values)
		self.transport.write(pd)

	def dataReceived(self,data):
		print "Receive"
		self.data = pickle.loads(data)
		
		if self.first == 0:
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
class CommandConnFactory(ClientFactory):
	def __init__(self,gs=None):
		self.gs = gs

    	def buildProtocol(self, addr):
		return CommandConn(self.gs)

    	def clientConnectionLost(self, connector, reason):
        	print 'Lost connection.  Reason:', reason

    	def clientConnectionFailed(self, connector, reason):
        	print 'Connection failed. Reason:', reason

class Joiner:
	def __init__(self, screen, address, port):
		self.screen = screen
		self.address = address
		self.port = port

	def start(self):
		#Initialize GameSpace
		gs = GameSpace(self.screen)
		gs.main()

		#Create Looping Call
		lc = LoopingCall(gs.gameLoop)
		lc.start(.0166666666)

		#Begin Connecting
		reactor.connectTCP(self.address,self.port,CommandConnFactory(gs))

if __name__ == '__main__':	
	sys.exit('trying running memory.py')

