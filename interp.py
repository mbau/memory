import pygame

class TimedInterpolator:
	def __init__(self, default=0):
		self.start(default,default)

	def start(self, begin, end, duration=1000):
		self.starttime = pygame.time.get_ticks()
		self.begin = begin
		self.end = end
		self.duration = duration

	def current(self):
		time = pygame.time.get_ticks() - self.starttime
		return sorted((self.begin,self.begin + (self.end - self.begin)*time/self.duration,self.end))[1]

