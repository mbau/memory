import pygame

from interp import TimedInterpolator

#
# Class that stores all of the values for a single card
#
class Card(pygame.sprite.Sprite):
	HORSE = 0
	MONKEY = 1
	GORILLA = 2
	SQUIRREL = 3
	BULL = 4
	BIRD = 5
	FISH = 6
	SPIDER = 7
	PIG = 8
	ROOSTER = 9
	DOG = 10
	TURTLE = 11

	FLIP_SOUND = None

	def __init__(self, gs=None,x=None,y=None,value=None):
		pygame.sprite.Sprite.__init__(self)

		if Card.FLIP_SOUND == None:
			Card.FLIP_SOUND = pygame.mixer.Sound('sounds/card_flip.wav')

		self.gs = gs #game board
		self.value = value #represents the card picture, either 0-11

		self.curFrame = 0 #counts frames during flipping
		self.Flip = False #True when card is being flipped
		self.flipduration = 1000 # Length of the flip animation
		self.flipDirection = 1 #Either 1 or -1 to determine which way to flip card
		self.selected = False #True when card is clicked and/or turned over
		self.matched = False #True when card has been matched

		self.image = pygame.image.load("card/flip0.jpg")
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x,y)
		self.xinterp = TimedInterpolator(self.rect.x)
		self.yinterp = TimedInterpolator(self.rect.y)
		self.loadflip()


	def loadflip(self):
		#Load all pictures in order for flip sequence and store in self.flip
		self.flip = list()
		for i in range(0,30):
			self.flip.append(pygame.image.load("card/flip"+str(i)+".jpg"))


	def select(self):
		self.selected = True
		self.startFlip()


	def startFlip(self):
		Card.FLIP_SOUND.play()

		self.Flip = True
		self.flipstart = pygame.time.get_ticks()


	def move(self, x, y):
		self.xinterp.start(self.rect.x,x,duration=2000)
		self.yinterp.start(self.rect.y,y,duration=2000)

		self.rect.x = x
		self.rect.y = y


	def tick(self):
		if self.matched:
			#Card is matched, display black image
			self.image = pygame.image.load("card/flip15.jpg")
		else:
			#If card is in process of flipping
			if self.Flip:
				ticks = pygame.time.get_ticks() - self.flipstart
				self.curFrame = max(1, min(30*ticks/self.flipduration,30))

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


	def draw(self, surface):
		surface.blit(self.image,(self.xinterp.current(), self.yinterp.current()))

