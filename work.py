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

#
# Class that stores all of the values for a single card
#
class Card(pygame.sprite.Sprite):
	def __init__(self, gs=None,x=None,y=None,value=None):
		pygame.sprite.Sprite.__init__(self)

		self.gs = gs #game board
		self.value = value #represents the card picture, either 0-11
		
		self.curFrame = 0 #counts frames during flipping
		self.Flip = False #True when card is being flipped
		self.flipDirection = 1 #Either 1 or -1 to determine which way to flip card
		self.selected = False #True when card is clicked and/or turned over
		self.matched = False #True when card has been matched

		self.image = pygame.image.load("card/flip0.jpg")
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x,y)
		self.loadflip()


	def loadflip(self):
		#Load all pictures in order for flip sequence and store in self.flip
		self.flip = list()
		for i in range(0,30):
			self.flip.append(pygame.image.load("card/flip"+str(i)+".jpg"))	


	def tick(self):
		if self.matched is True:
			#Card is matched, display black image
			self.image = pygame.image.load("card/flip15.jpg")
		else:
			#If card is in process of flipping
			if self.Flip is True:	

				self.curFrame+=1
				if self.flipDirection > 0:
					if self.curFrame >=30:
						#Flip is complete
						#Display card image
						self.image = pygame.image.load("card/card"+str(self.value)+".png")

						self.Flip = False #Stop flipping
						self.flipDirection*=-1 #Change direction for next time
						self.curFrame = 0 #Reset
					else:
						#Display next image
						self.image = self.flip[self.curFrame]
				else: 
					if self.curFrame >=30:
						#Flip is complete
						#Display back of card
						self.image = pygame.image.load("card/flip0.jpg")

						self.Flip = False #Stop flipping
						self.flipDirection*=-1 #Change direction for next time
						self.curFrame = 0 #reset
					else:
						#Display next image
						self.image = self.flip[30 - self.curFrame]



#
# Class that stores game board state
#
class GameSpace:
	def main(self):
		#Basic Initializations
		pygame.init()

		self.size = self.width, self.height = 970, 800
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

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
# This class is a wrapper for all of the variables for the
# game. Class is pickled and then sent and received over the 
# connection in order to communicate the game state
#
class Values():
	def __init__(self):

		#Card Dictionaries
		self.card_curFrame = dict()
		self.card_Flip = dict()
		self.card_flipDirection = dict()
		self.card_selected = dict()
		self.card_matched = dict()
		self.card_value = dict()

		#GS Values
		self.firstCard = 0
		self.message = ""
		self.p1 = 0
		self.p2 = 0
		self.turn = 1
		self.timer = 0
		self.startTimer = False

		#card values initiated
		for i in range(0,24):
			self.card_curFrame[i] = 0
			self.card_Flip[i] = False
			self.card_flipDirection[i] = 1
			self.card_selected[i] = False
			self.card_matched[i] = False
			self.card_value[i] = -1


	def save(self,gs):
		# Save all GS values
		self.firstCard = gs.firstCard
		self.message = gs.message
		self.p1 = gs.p1
		self.p2 = gs.p2
		self.turn = gs.turn
		self.timer = gs.timer
		self.startTimer = gs.startTimer

		# Save all card values
		for i in range(0,24):
			self.card_curFrame[i] = gs.card_list[i].curFrame
			self.card_Flip[i] = gs.card_list[i].Flip
			self.card_flipDirection[i] = gs.card_list[i].flipDirection
			self.card_selected[i] = gs.card_list[i].selected
			self.card_matched[i] = gs.card_list[i].matched
			self.card_value[i] = gs.card_list[i].value


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



if __name__ == '__main__':	
	# Process command-line arguments
	address = sys.argv[1]
	port = int(sys.argv[2])

	#Initialize GameSpace
	gs = GameSpace()
	gs.main()

	#Create Looping Call
	lc = LoopingCall(gs.gameLoop)
	lc.start(.0166666666)

	#Begin Connecting
	reactor.connectTCP(address,port,CommandConnFactory(gs))
	reactor.run()


