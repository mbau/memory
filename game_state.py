import pygame
import random
import sys

from card import Card

#
# Class that stores game board state
#
class GameState:
	def __init__(self, screen, player):
		self.screen = screen
		self.player = player

		self.size = self.width, self.height = self.screen.get_size()
		self.black = 0, 0, 0

		#Basic Initializations
		self.firstCard = 0 #Stores number of cards that have been selected
		self.message = "P1 turn" #Whose turn is it?
		self.p1 = 0 #Score
		self.p2 = 0 #Score
		self.turn = 1 # Player whose turn it is
		self.command = None #Stores the CommandConn class
		self.timer = 0 #Used to track time after 2 cards are selected
		self.startTimer = False #True when time is on
		self.start = self.player != 1 #True when Player 2 is connected
		self.GameOver = False

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
		if self.start is True:
			#If a player 2 is connected, then display main screen
			self.loop()
		else:
			#Otherwise display waiting screen
			self.waiting()


	def waiting(self):
		#Handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.command.transport.loseConnection()
				pygame.quit()
       				sys.exit()

		#Create labels
		myfont = pygame.font.SysFont("monospace",30)
		self.label = myfont.render("Memory",1,(250,215,0))
		self.player1 = myfont.render("Player 1: "+str(self.p1),1,(250,215,0))
		self.player2 = myfont.render("Player 2: "+str(self.p2),1,(250,215,0))
		self.gameover = myfont.render("WAITING FOR PLAYER 2",3,(250,215,0))

		self.screen.fill(self.black)

		#Display labels
		self.screen.blit(self.label,(430,30))
		self.screen.blit(self.player1,(20,30))
		self.screen.blit(self.player2,(750,30))
		self.screen.blit(self.gameover,(300,400))

		pygame.display.flip()


	def loop(self):
		# handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				if self.command != None:
					self.command.transport.loseConnection()
				pygame.quit()
       				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				#User clicks card and it is his/her turn
				if self.turn == self.player:
					for i in self.card_list.keys():
						if(self.card_list[i].rect.collidepoint(pygame.mouse.get_pos())):
							#As long as 2 cards have not already been selected,
							#and the card clicked is not already matched or already selected, then flip it
							if self.startTimer is not True and self.card_list[i].matched is False and self.card_list[i].selected is False:
								self.card_list[i].Flip = True
								self.card_list[i].selected = True
								self.firstCard+=1
				else:
					print "Not Your Turn"

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
						if self.turn == 1:
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
			self.turn = 2 if self.turn == 1 else 1

			if self.turn == 1:
				self.message = "P1 turn"
			else:
				self.message = "P2 turn"

			if self.turn != self.player:
				#Tell the other player it's their turn
				self.command.send()

		# send a tick to every game object!
		for i in self.card_list.keys():
			self.card_list[i].tick()

		# Set labels
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

		#If it is our turn, then send game state to the other player
		if self.command != None and self.turn == self.player:
			self.command.send()

