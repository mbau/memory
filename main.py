import math
import pygame
import os, sys
from pygame.locals import *
import random
import pickle

class Card(pygame.sprite.Sprite):
	def __init__(self, gs=None,x=None,y=None,value=None):
		pygame.sprite.Sprite.__init__(self)

		self.gs = gs
		self.value = value
		self.image = pygame.image.load("card/flip0.jpg")
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(x,y)
		self.loadflip()
		self.curFrame = 0
		self.value = value
		self.Flip = False
		self.flipDirection = 1
		self.selected = False
		self.matched = False


	def loadflip(self):
		self.flip = list()
		for i in range(0,30):
			self.flip.append(pygame.image.load("card/flip"+str(i)+".jpg"))	

	def tick(self):
		if self.matched is True:
			self.image = pygame.image.load("card/flip15.jpg")
		else:
			if self.Flip is True:
				self.curFrame+=1
			
				if self.flipDirection > 0:
					if self.curFrame >=30:
						self.image = pygame.image.load("card/card"+str(self.value)+".jpg")
						self.Flip = False
						self.flipDirection*=-1
						self.curFrame = 0
					else:
						self.image = self.flip[self.curFrame]
				else: 
					if self.curFrame >=30:
						self.image = pygame.image.load("card/flip0.jpg")
						self.Flip = False
						self.flipDirection*=-1
						self.curFrame = 0
					else:
						self.image = self.flip[30 - self.curFrame]




class GameSpace:
	def main(self):
		# 1) basic initializations
		pygame.init()

		self.size = self.width, self.height = 970, 800
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		# 2) set up game objects
		self.clock = pygame.time.Clock()

		self.firstCard = 0
		self.message = "P1 turn"
		self.p1 = 0
		self.p2 = 0
		self.turn = 1
		self.GameOver = False

		#initialize card dictionary
		self.cards = dict()
		for i in range(0,12):
			self.cards[i] = 0
		
		self.card_list = pygame.sprite.Group()
		width = -150
		height = 80
		for i in range(0,24):
			if i % 4 == 0:
				width = width + 160
				height = 100
			
			self.card_list.add(Card(self,width,height,self.getValue()))
			height = height + 160
		
		# 3) start game loop
		while 1:
			# 4) clock tick regulations (framerate)
			self.clock.tick(60)
	
			# 5) this is where you would handle user inputs...
			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
               				sys.exit()
				if event.type == MOUSEBUTTONDOWN and event.button == 1:
					for i in self.card_list:
						#check if card has been clicked
						if(i.rect.collidepoint(pygame.mouse.get_pos())):
							#flip the card over
							if self.startTimer is not True and i.matched is False:
								i.Flip = True
								i.selected = True
								self.firstCard+=1

			if self.firstCard == 2:
				self.startTimer = True
			else:
				self.startTimer = False

			if self.startTimer is True:
				self.timer+=1
			else:
				self.timer = 0

			if self.timer > 180:
				for i in self.card_list:
					for j in self.card_list:
						if i.selected is True and j.selected is True and i.value == j.value and i != j:
							i.matched = True
							j.matched = True
							j.selected = False
							i.selected = False
							if self.turn > 0:
								self.p1+=1
							else:
								self.p2+=1

							self.firstCard = 0
							self.startTimer = False
						if i.selected is True and j.selected is True and i != j:
							i.Flip = True
							j.Flip = True
							j.selected = False
							i.selected = False
							self.firstCard = 0
							self.startTimer = False
				self.turn*=-1
				if self.turn > 0:
					self.message = "P1 turn"
				else:
					self.message = "P2 turn"
						
								
												

			# 6) send a tick to every game object!
			for i in self.card_list:
				i.tick()

			myfont = pygame.font.SysFont("monospace",30)
			self.label = myfont.render("Memory ",1,(250,215,0))
			self.turnlabel = myfont.render(str(self.message),1,(250,215,0))
			self.player1 = myfont.render("Player 1: "+str(self.p1),1,(250,215,0))
			self.player2 = myfont.render("Player 2: "+str(self.p2),1,(250,215,0))
			self.gameover = myfont.render("WAITING FOR PLAYER 2",3,(250,215,0))

			# 7) and finally, display the game objects
			self.screen.fill(self.black)

			for i in self.card_list:
				self.screen.blit(i.image,i.rect)

			#display labels
			self.screen.blit(self.label,(430,30))
			self.screen.blit(self.player1,(20,30))
			self.screen.blit(self.player2,(750,30))
			self.screen.blit(self.turnlabel,(430,750))

			self.GameOver = True
			for i in self.card_list:
				if i.matched is False:
					self.GameOver = False

				self.screen.blit(self.gameover,(300,400))

			pygame.display.flip()

	def getValue(self):
		x = 0
		y = 0
		while y == 0:
			x = random.randint(0,11)
			if(self.cards[x] < 2):
				self.cards[x]+=1
				y = 1
		return x




if __name__ == '__main__':
	gs = GameSpace()
	gs.main()