import pygame

from pygame.rect import Rect

class BonusTimer:
	def __init__(self, duration, rect):
		self.duration = duration
		self.rect = rect

		self.backcolor = 50, 50, 50, 50
		self.curtime = 0

		self.stop()
		self.reset()

		bar = pygame.image.load('bonus_bar.png')
		self.barleft = pygame.transform.smoothscale(bar.subsurface(Rect(0,0,12,24)),
			(self.rect.h*12/24, self.rect.h))
		self.barmid = pygame.transform.smoothscale(bar.subsurface(Rect(12,0,1,24)),
			(self.rect.h*1/24, self.rect.h))
		self.barright = pygame.transform.smoothscale(bar.subsurface(Rect(13,0,12,24)),
			(self.rect.h*12/24, self.rect.h))

		font = pygame.font.SysFont('monospace',self.rect.h,bold=True)
		self.textsurf = font.render('BONUS',True,(50, 50, 255))

	def setDuration(self, duration):
		self.duration = duration

	def reset(self, starttime=None):
		self.starttime = pygame.time.get_ticks() if starttime == None else starttime
		self.progress = 0

	def start(self):
		self.running = True

	def stop(self):
		self.running = False

	def update(self, time=None):
		self.curtime = pygame.time.get_ticks() if time == None else time

		if self.running or time != None:
			self.progress = min(float(self.curtime - self.starttime)/self.duration,1)

	def tick(self):
		self.update()

	def draw(self, screen):
		leftx = self.rect.x + self.barleft.get_width()
		midwidth = self.rect.w - self.barleft.get_width() - self.barright.get_width()
		rightx = leftx + int((1 - self.progress)*midwidth)

		midscaled = pygame.transform.smoothscale(self.barmid,(rightx - leftx, self.rect.h))

		textpos = (self.rect.x + (self.rect.w - self.textsurf.get_width())/2,
			self.rect.y + (self.rect.h - self.textsurf.get_height())/2)

		screen.blit(self.barleft,self.rect.topleft)
		screen.blit(midscaled,(leftx, self.rect.y))
		screen.blit(self.barright,(rightx, self.rect.y))
		screen.blit(self.textsurf,textpos)

