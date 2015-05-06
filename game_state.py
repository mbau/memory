import pygame
import random
import sys

import main_screen

from pygame.rect import Rect

from twisted.internet import reactor

from bonus_timer import BonusTimer
from card import Card
from interp import TimedInterpolator
from powers import Power
from widgets import Button

#
# Class that stores game board state
#
class GameState:
	def __init__(self, owner, screen, player, inqueue, outqueue):
		# Knowledge about the outside world
		self.owner = owner
		self.screen = screen
		self.player = player
		self.inqueue = inqueue
		self.outqueue = outqueue

		# UI configuration
		self.size = self.width, self.height = self.screen.get_size()
		self.black = 0, 0, 0
		self.yellow = 250, 215, 0

		# Game status tracking
		self.start = False
		self.cards = []
		self.selected = []
		self.timestart = 0

		# Special flags to allow for the powers to function
		self.matchallowed = True
		self.doneselecting = False
		self.skipturn = False

		# Set up the bonus timer
		self.maxbonus = 10000
		self.bonusdurations = {1: 5000, 2: 5000}
		self.bonus = BonusTimer(5000,Rect(600,750,330,25))

		# Set up the powers
		self.powers = []
		self.powersallowed = True
		for i in xrange(12):
			self.powers.append(Power(self,i))

		# Allow us to go back to the menu after a game
		self.menubutton = Button('Return to Menu',Rect(335,430,300,25),self.gotoMenu,fgcolor=self.yellow)

		# Network initialization
		self.inqueue.get().addCallback(self.gotMessage)

		# Let player 1 be authoritative on the ordering of the cards
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
		self.turncount = 0
		self.GameOver = False

		#Create labels
		self.myfont = pygame.font.SysFont("monospace",30)
		self.label = self.myfont.render("Memory",1,self.yellow)
		self.turnlabel = self.myfont.render(str(self.message),1,self.yellow)
		self.player1 = self.myfont.render("Player 1: "+str(self.p1),1,self.yellow)
		self.player2 = self.myfont.render("Player 2: "+str(self.p2),1,self.yellow)
		self.gameover = self.myfont.render("WAITING FOR PLAYER 2",3,self.yellow)
		self.winsurf = self.myfont.render('You Win!',True,self.yellow)
		self.tiesurf = self.myfont.render('It\'s a Tie!',True,self.yellow)
		self.losesurf = self.myfont.render('You Lose!',True,self.yellow)

	# Code for handling a message (probably from the other player, across
	# the network, but we don't really care either way).
	def gotMessage(self, msg):
		# All commands are text-based, with arguments and such seperated by single spaces
		cmd = msg.split(' ')

		try:
			if cmd[0] == 'connection_made': # Signal to start the game proper
				self.start = True

				if self.turn == self.player:
					self.bonus.reset()
					self.bonus.start()

					self.outqueue.put('turn ' + str(self.bonus.starttime))
			elif cmd[0] == 'card_order': # Player 2 learning the answers
				if self.player == 1:
					print 'card ordering received from a player other than player 1'
				elif self.cards:
					print 'already have a card ordering'
				else: self.initializeCards(int(x) for x in cmd[1:25])
			elif cmd[0] == 'turn': # Synchronize the bonus timers
				if self.turn == self.player:
					print 'turn message received on own turn'
				else:
					starttime = int(cmd[1])
					self.bonus.reset(starttime=starttime)
			elif cmd[0] == 'select_card': # Let the other player know which card you picked
				if self.turn == self.player:
					print 'received card selection message on own turn'
				else:
					ticks = int(cmd[1])
					self.bonus.update(time=ticks)

					i = int(cmd[2])
					self.selectCard(i,notify=False)
			# All of the below are commands associated with powers; c.f. powers.py
			elif cmd[0] == 'fast_bonus':
				self.powers[Card.HORSE].activate(evil=True)
			elif cmd[0] == 'scramble_cards':
				self.powers[Card.MONKEY].activate(evil=True)
			elif cmd[0] == 'skip_turn':
				self.powers[Card.GORILLA].activate(evil=True)
			elif cmd[0] == 'extra_points':
				self.addPoints(1000)
				self.powers[Card.SQUIRREL].activate(evil=True)
			elif cmd[0] == 'disable_powers':
				self.powers[Card.BULL].activate(evil=True)
			elif cmd[0] == 'show_cards':
				self.powers[Card.BIRD].activate(evil=True)
			elif cmd[0] == 'erq_ureevat':
				self.powers[Card.FISH].activate(evil=True)
			elif cmd[0] == 'replenish_cards':
				# Reset (most) cards
				for card in self.cards:
					if card.value != Card.SPIDER:
						card.__init__(self,card.rect.x,card.rect.y,card.value)

				self.scrambleCards()

				# Also reset (most) powers
				for power in self.powers:
					if power.value != Card.SPIDER:
						power.setAvailable(False)
			elif cmd[0] == 'sniff':
				if not self.doneselecting and len(self.selected) == 1:
					for i, card in enumerate(self.cards):
						if card.value == self.selected[0].value and card is not self.selected[0]:
							self.selectCard(i)

				if self.turn != self.player:
					self.powers[Card.PIG].activate(evil=True)
			elif cmd[0] == 'replenish_card':
				value = int(cmd[1])

				for card in filter(lambda c: c.value in (Card.ROOSTER, value),self.cards):
					card.__init__(self,card.rect.x,card.rect.y,card.value)

				self.scrambleCards()

				self.powers[Card.ROOSTER].activate(evil=True)
			elif cmd[0] == 'steal_points':
				if self.turn == 1:
					points = 0.1*self.p2
					self.addPoints( points,player=1)
					self.addPoints(-points,player=2)
				else:
					points = 0.1*self.p1
					self.addPoints(-points,player=1)
					self.addPoints( points,player=2)
			elif cmd[0] == 'slow_bonus':
				self.powers[Card.TURTLE].activate(evil=True)
			else: print 'unknown command: ' + cmd[0]
		except (IndexError, ValueError):
			print 'bad command received: ' + msg

		# Ask for the next one form our DeferredQueue
		self.inqueue.get().addCallback(self.gotMessage)

	# Calculate the n-th layout position for a card
	def cardPosition(self, n):
		topleft = 10, 100
		hspacing = 160
		vspacing = 160
		ncols = 6

		x = topleft[0] + n%ncols*hspacing
		y = topleft[1] + n/ncols*vspacing

		return x, y

	# Determine the official order of the cards for this game
	def arrangeCards(self):
		# Two of each of the twelve cards
		self.initializeCards(random.sample(list(n/2 for n in xrange(24)),24))

		# Tell the other player
		self.outqueue.put('card_order ' + ' '.join(str(c.value) for c in self.cards))

	# Don't change the in-memory order of the cards, only the on-screen arrangement
	def scrambleCards(self):
		order = iter(random.sample(range(24),24))

		for card in self.cards:
			pos = self.cardPosition(next(order))
			card.move(pos[0],pos[1])

	# Actually construct and place the cards
	def initializeCards(self, ids):
		self.cards = []

		# Card arrangement
		n = 0
		for i in ids:
			pos = self.cardPosition(n)
			self.cards.append(Card(self,pos[0],pos[1],i))

			n += 1

	# As long as 2 cards have not already been selected,
	# and the card clicked is not already matched
	# or already selected, then flip it.
	def selectCard(self, i, notify=True):
		card = self.cards[i]

		if not self.doneselecting and not card.matched and not card.selected:
			card.select()
			self.selected.append(card)

			self.timestart = pygame.time.get_ticks()

			self.doneselecting |= len(self.selected) >= 2

		if self.doneselecting:
			self.bonus.stop()

		# Tell the other player
		if notify:
			self.outqueue.put('select_card ' + str(self.bonus.curtime) + ' ' + str(i))

	# Change the score of a player (the current player, by default)
	def addPoints(self, points, player=None):
		points = int(points)

		if player == 1 or self.turn == 1:
			self.p1interp.start(self.p1,self.p1 + points,2000)
			self.p1 += points
		else:
			self.p2interp.start(self.p2,self.p2 + points,2000)
			self.p2 += points

	# Adieu
	def gotoMenu(self):
		self.owner.stop(main_screen.MainScreen(self.screen))

	# The main game logic, called sixty times a second (assuming Twisted is reliable)
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

					if not self.doneselecting and self.powersallowed:
						for power in self.powers:
							if power.rect.collidepoint(pygame.mouse.get_pos()):
								power.activate()

				if self.GameOver:
					self.menubutton.click(event.button,event.pos)

		#After 3 seconds, update score, switch turn and flip cards back over
		if self.doneselecting and pygame.time.get_ticks() - self.timestart > 3000:
			#The 2 cards are a match
			if self.matchallowed and self.selected[0].value == self.selected[1].value:
				for card in self.selected:
					card.matched = True
					card.selected = False

				# Activate the power
				if self.turn == self.player:
					self.powers[self.selected[0].value].setAvailable(True)

				# Update score
				self.addPoints(100 + int((1 - self.bonus.progress)*self.maxbonus))
			else: #The 2 cards are not a match
				#Flip the cards back over
				for card in self.selected:
					card.startFlip()
					card.selected = False

			# Reset the selection for the next turn
			self.selected = []
			self.matchallowed = True
			self.doneselecting = False

			#Change turns
			for _ in xrange(2 if self.skipturn else 1):
				self.bonusdurations[self.turn] = self.bonus.duration

				self.turn = 2 if self.turn == 1 else 1
				self.turncount += 1

				self.bonus.setDuration(self.bonusdurations[self.turn])

			# Reset the bonus timer
			self.bonus.stop()
			self.bonus.reset()
			if self.turn == self.player:
				self.bonus.start()

			# Synchronize with the other player
			if self.turn == self.player:
				self.outqueue.put('turn ' + str(self.bonus.starttime))

			# Update the on-screen message
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

		# Update the on-screen labels
		self.turnlabel = self.myfont.render(str(self.message),1,self.yellow)
		self.player1 = self.myfont.render("Player 1: "+str(self.p1interp.current()),1,self.yellow)
		self.player2 = self.myfont.render("Player 2: "+str(self.p2interp.current()),1,self.yellow)

		#Make screen black
		self.screen.fill(self.black)

		#display cards
		for card in self.cards:
			card.draw(self.screen)

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

		# Check for the endgame condition -- all cards matched
		self.GameOver = bool(self.cards)
		for card in self.cards:
			if card.matched is False:
				self.GameOver = False

		# If game over, display a message
		if self.GameOver:
			if self.p1 == self.p2:
				self.screen.blit(self.tiesurf,(400, 400))
			elif (self.p1 > self.p2) == (self.player == 1):
				self.screen.blit(self.winsurf,(400, 400))
			else: self.screen.blit(self.losesurf,(400, 400))

			self.menubutton.draw(self.screen)

		pygame.display.flip()

