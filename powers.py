import pygame

from pygame.rect import Rect

class Power:
	GLOW_IMAGE = pygame.image.load('icons/glow.png')

	def __init__(self, value):
		self.value = value

		self.active = False
		self.available = False

		self.image = pygame.image.load('icons/icon' + str(self.value) + '.png')
		self.rect = Rect((20 + self.value*31, 752),self.image.get_size())

	def setAvailable(self, available):
		self.available = available

	def activate(self):
		self.active = True

	def tick(self):
		pass

	def draw(self, screen):
		if self.active:
			glowx = self.rect.x + (self.rect.w - Power.GLOW_IMAGE.get_width())/2
			glowy = self.rect.y + (self.rect.h - Power.GLOW_IMAGE.get_height())/2
			screen.blit(Power.GLOW_IMAGE,(glowx, glowy))

		if self.available:
			screen.blit(self.image,self.rect)
		else:
			# Faded-out icon
			temp = pygame.Surface(self.image.get_size())
			temp.blit(screen,(-self.rect.x, -self.rect.y))
			temp.blit(self.image, (0, 0))
			temp.set_alpha(100)
			screen.blit(temp,self.rect)

