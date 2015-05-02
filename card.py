import pygame

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

