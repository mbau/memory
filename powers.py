import pygame
import random

from pygame.rect import Rect

from card import Card

class Power:
	GLOW_IMAGE = pygame.image.load('icons/glow.png')
	EVIL_IMAGE = pygame.image.load('icons/evil.png')

	def __init__(self, gs, value):
		self.gs = gs
		self.value = value

		self.active = False
		self.available = False

		self.image = pygame.image.load('icons/icon' + str(self.value) + '.png')
		self.rect = Rect((20 + self.value*31, 752),self.image.get_size())

	def setAvailable(self, available):
		self.available = available

	def activate(self, evil=False):
		if self.active or not self.available and not evil:
			return

		self.active = True
		self.activeevil = evil
		self.activeturn = self.gs.turncount

		if self.value == Card.HORSE: # Less bonus time for other player
			self.gs.bonusdurations[2 if self.gs.turn == 1 else 1] *= 0.5

			if not self.activeevil:
				self.gs.outqueue.put('fast_bonus')
		elif self.value == Card.MONKEY: # Scramble the other player's cards
			self.setAvailable(False)

			if self.activeevil:
				self.gs.scrambleCards()
			else: self.gs.outqueue.put('scramble_cards')
		elif self.value == Card.GORILLA: # Skip the other player's next turn
			self.gs.skipturn = True

			if not self.activeevil:
				self.gs.outqueue.put('skip_turn')
		elif self.value == Card.SQUIRREL: # Extra points!
			if not self.activeevil:
				self.gs.inqueue.put('extra_points')
				self.gs.outqueue.put('extra_points')
		elif self.value == Card.BULL: # Prevent the other side from using powers
			if self.activeevil:
				self.gs.powersallowed = False
			else: self.gs.outqueue.put('disable_powers')
		elif self.value == Card.BIRD: # Show half of the remaining cards
			self.gs.matchallowed = False
			self.gs.doneselecting = True
			self.gs.timestart = pygame.time.get_ticks()

			if not self.activeevil:
				self.gs.bonus.stop()

				evens = random.randint(0,1)
				for i, card in enumerate(filter(lambda c: not c.matched,self.gs.cards)):
					if (i + evens)%2:
						card.select()
						self.gs.selected.append(card)

				self.gs.outqueue.put('show_cards')
		elif self.value == Card.FISH: # Win
			if not self.activeevil:
				self.activeevil = True
				self.gs.outqueue.put('erq_ureevat')
		elif self.value == Card.SPIDER: # Reset (most) cards
			self.gs.inqueue.put('replenish_cards')
			self.gs.outqueue.put('replenish_cards')
		elif self.value == Card.PIG: # Chance of auto-matching a card
			if not self.activeevil and random.random() < 0.67:
				self.gs.inqueue.put('sniff')
				self.gs.outqueue.put('sniff')
		elif self.value == Card.ROOSTER: # Reset this and one other pair
			if not self.activeevil:
				try: value = random.choice(filter(lambda c: c.matched and c.value != Card.ROOSTER,self.gs.cards)).value
				except IndexError: value = Card.ROOSTER

				self.gs.inqueue.put('replenish_card ' + str(value))
				self.gs.outqueue.put('replenish_card ' + str(value))
		elif self.value == Card.DOG: # Steal 10% of the other player's points
			if not self.activeevil:
				self.gs.inqueue.put('steal_points')
				self.gs.outqueue.put('steal_points')
		elif self.value == Card.TURTLE: # More bonus time
			self.gs.bonusdurations[self.gs.turn] *= 2

			if not self.activeevil:
				self.gs.outqueue.put('slow_bonus')

	def tick(self):
		if not self.active:
			return

		nturns = self.gs.turncount - self.activeturn

		if self.value == Card.HORSE: # Last two turns
			if nturns > 3:
				self.gs.bonusdurations[2 if self.gs.turn == 1 else 1] /= 0.5

				self.setAvailable(False)
				self.active = False
		elif self.value == Card.MONKEY: # Permanent
			pass
		elif self.value == Card.GORILLA: # Last one turn
			if nturns > 2:
				self.setAvailable(False)
				self.active = False

			if nturns > 1:
				self.gs.skipturn = False
		elif self.value == Card.SQUIRREL: # Last one turn
			if nturns > 0:
				self.active = False
		elif self.value == Card.BULL: # Last two turns
			if nturns > 3:
				if self.activeevil:
					self.gs.powersallowed = True

				self.setAvailable(False)
				self.active = False
		elif self.value == Card.BIRD: # Last one turn
			if nturns > 0:
				self.setAvailable(False)
				self.active = False
		elif self.value == Card.FISH: # Permanent
			pass
		elif self.value == Card.SPIDER: # Permanent
			self.setAvailable(False)
		elif self.value == Card.PIG: # Last one turn
			if nturns > 1:
				self.setAvailable(False)
				self.active = False
		elif self.value == Card.ROOSTER: # Last one turn
			if nturns > 0:
				self.setAvailable(False)
				self.active = False
		elif self.value == Card.DOG: # Last one turn
			if nturns > 0:
				self.setAvailable(False)
				self.active = False
		elif self.value == Card.TURTLE: # Last two turns
			if nturns > 2:
				self.gs.bonusdurations[self.gs.turn] /= 2

				self.setAvailable(False)
				self.active = False

	def draw(self, screen):
		if self.active:
			glowx = self.rect.x + (self.rect.w - Power.GLOW_IMAGE.get_width())/2
			glowy = self.rect.y + (self.rect.h - Power.GLOW_IMAGE.get_height())/2
			if self.activeevil:
				screen.blit(Power.EVIL_IMAGE,(glowx, glowy))
			else: screen.blit(Power.GLOW_IMAGE,(glowx, glowy))

		if self.available:
			screen.blit(self.image,self.rect)
		else:
			# Faded-out icon
			temp = pygame.Surface(self.image.get_size())
			temp.blit(screen,(-self.rect.x, -self.rect.y))
			temp.blit(self.image,(0, 0))
			temp.set_alpha(100)
			screen.blit(temp,self.rect)

