import pygame
import random
import sys

from pygame.rect import Rect

from twisted.internet import reactor

from bonus_timer import BonusTimer
from card import Card
from interp import TimedInterpolator
from powers import Power

#
# Class that stores game board state
#
class GameState:
	def __init__(self, screen, player, inqueue, outqueue):
		self.screen = screen
		self.player = player
		self.inqueue = inqueue
		self.outqueue = outqueue

		self.size = self.width, self.height = self.screen.get_size()
		self.black = 0, 0, 0

		self.start = False
		self.cards = []
		self.selected = []
		self.timestart = 0

		self.maxbonus = 10000
		self.bonus = BonusTimer(5000,Rect(600,750,330,25))

		self.powers = []
		for i in xrange(12): self.powers.append(Power(i))

		# Network initialization
		self.inqueue.get().addCallback(self.gotMessage)

		if self.player == 1:
			self.arrangeCards()

		#Basic Initializations
		self.firstCard = 0 #Stores number of cards that have been selected
		self.message = "P1 turn" #Whose turn is it?
		self.p1 = 0 #Score
		self.p2 = 0 #Score
		self.p1interp = TimedInterpolator()
		self.p2interp = TimedInterpolator()
		self.turn = 1 # Player whose turn it is
		self.GameOver = False

		#Create labels
		myfont = pygame.font.SysFont("monospace",30)
		self.label = myfont.render("Memory",1,(250,215,0))
		self.player1 = myfont.render("Player 1: "+str(self.p1),1,(250,215,0))
		self.player2 = myfont.render("Player 2: "+str(self.p2),1,(250,215,0))
		self.gameover = myfont.render("WAITING FOR PLAYER 2",3,(250,215,0))

	def gotMessage(self, msg):
		cmd = msg.split(' ')

		try:
			if cmd[0] == 'connection_made':
				self.start = True

				if self.turn == self.player:
					self.bonus.reset()
					self.bonus.start()

					self.outqueue.put('turn ' + str(self.bonus.starttime))
			elif cmd[0] == 'card_order':
				if self.player == 1:
					print 'card ordering received from a player other than player 1'
				elif self.cards:
					print 'already have a card ordering'
				else: self.initializeCards(int(x) for x in cmd[1:25])
			elif cmd[0] == 'turn':
				if self.turn == self.player:
					print 'turn message received on own turn'
				else:
					starttime = int(cmd[1])
					self.bonus.reset(starttime=starttime)
			elif cmd[0] == 'select_card':
				if self.turn == self.player:
					print 'received card selection message on own turn'
				else:
					ticks = int(cmd[1])
					self.bonus.update(time=ticks)

					i = int(cmd[2])
					self.selectCard(i)
			else: print 'unknown command: ' + cmd[0]
		except (IndexError, ValueError):
			print 'bad command received: ' + msg

		self.inqueue.get().addCallback(self.gotMessage)

	def arrangeCards(self):
		# Two of each of the twelve cards
		self.initializeCards(random.sample(list(n/2 for n in xrange(24)),24))

		# Tell the other player
		self.outqueue.put('card_order ' + ' '.join(str(c.value) for c in self.cards))

	def initializeCards(self, ids):
		self.cards = []

		# Card arrangement
		topleft = 10, 100
		hspacing = 160
		vspacing = 160
		ncols = 6

		n = 0
		for i in ids:
			x = topleft[0] + n%ncols*hspacing
			y = topleft[1] + n/ncols*vspacing

			self.cards.append(Card(self,x,y,i))

			n += 1

	# As long as 2 cards have not already been selected,
	# and the card clicked is not already matched
	# or already selected, then flip it.
	def selectCard(self, i):
		card = self.cards[i]

		if len(self.selected) < 2 and not card.matched and not card.selected:
			card.select()
			self.selected.append(card)

			self.timestart = pygame.time.get_ticks()

		if len(self.selected) == 2:
			self.bonus.stop()

	def gameLoop(self):
		if self.start:
			#If a player 2 is connected, then display main screen
			self.loop()
		else:
			#Otherwise display waiting screen
			self.waiting()

	def waiting(self):
		#Handle user inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				reactor.stop()

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
				reactor.stop()
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				# Check for clicks on game objects
				if self.turn == self.player:
					for i, card in enumerate(self.cards):
						if card.rect.collidepoint(pygame.mouse.get_pos()):
							self.selectCard(i)

							# Tell the other player
							self.outqueue.put('select_card ' + str(self.bonus.curtime) + ' ' + str(i))

					for power in self.powers:
						if power.rect.collidepoint(pygame.mouse.get_pos()):
							power.activate()

		#After 3 seconds, update score, switch turn and flip cards back over
		if len(self.selected) == 2 and pygame.time.get_ticks() - self.timestart > 3000:
			#The 2 cards are a match
			if self.selected[0].value == self.selected[1].value:
				self.selected[0].matched = True
				self.selected[1].matched = True
				self.selected[0].selected = False
				self.selected[1].selected = False

				# Activate the power
				if self.turn == self.player:
					self.powers[self.selected[0].value].setAvailable(True)

				#Update score
				score = 100 + int((1 - self.bonus.progress)*self.maxbonus)
				if self.turn == 1:
					self.p1interp.start(self.p1,self.p1 + score,2000)
					self.p1 += score
				else:
					self.p2interp.start(self.p2,self.p2 + score,2000)
					self.p2 += score
			else: #The 2 cards are not a match
				#Flip the cards back over
				self.selected[0].startFlip()
				self.selected[1].startFlip()
				self.selected[0].selected = False
				self.selected[1].selected = False

			self.selected = []

			#Change turns
			self.turn = 2 if self.turn == 1 else 1

			self.bonus.stop()
			self.bonus.reset()
			if self.turn == self.player:
				self.bonus.start()

			if self.turn == self.player:
				self.outqueue.put('turn ' + str(self.bonus.starttime))

			if self.turn == 1:
				self.message = "P1 turn"
			else:
				self.message = "P2 turn"

		# send a tick to every game object!
		for card in self.cards:
			card.tick()

		for power in self.powers:
			power.tick()

		self.bonus.tick()

		# Set labels
		myfont = pygame.font.SysFont("monospace",30)
		self.label = myfont.render("Memory ",1,(250,215,0))
		self.turnlabel = myfont.render(str(self.message),1,(250,215,0))
		self.player1 = myfont.render("Player 1: "+str(self.p1interp.current()),1,(250,215,0))
		self.player2 = myfont.render("Player 2: "+str(self.p2interp.current()),1,(250,215,0))
		self.gameover = myfont.render("GAME OVER",3,(250,215,0))

		#Make screen black
		self.screen.fill(self.black)

		#display cards
		for card in self.cards:
			self.screen.blit(card.image,card.rect)

		# Draw the power icons
		for power in self.powers:
			power.draw(self.screen)

		# Draw the bonus timer
		self.bonus.draw(self.screen)

		#display labels
		self.screen.blit(self.label,(430,30))
		self.screen.blit(self.player1,(20,30))
		self.screen.blit(self.player2,(950 - self.player2.get_width(),30))
		self.screen.blit(self.turnlabel,(430,750))

		#Check if game over
		self.GameOver = bool(self.cards)
		for card in self.cards:
			if card.matched is False:
				self.GameOver = False

		#If game over, display words
		if self.GameOver is True:
			self.screen.blit(self.gameover,(400,400))

		pygame.display.flip()

