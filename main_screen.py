#
# Allows for network and game configuration.
#

import pygame

from home import Hoster

from pygame.rect import Rect

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from widgets import Button, InputField, TextLabel
from work import Joiner

class MainScreen:
	def __init__(self, screen):
		self.screen = screen

		self.targetfps = 60
		self.black = 0, 0, 0

		self.looping = LoopingCall(self.tick)

		self.addressfield = InputField('Server Address:',Rect(235,585,500,25),text='localhost')
		self.portfield = InputField('Server Port:',Rect(235,615,500,25),text='40100',numeric=True)

		self.errorlabel = TextLabel('',(235, 645),25,fgcolor=(255, 0, 0))

		self.hostbutton = Button('Host a Game',Rect(40,710,270,50),self.host)
		self.joinbutton = Button('Join a Game',Rect(350,710,270,50),self.join)
		self.quitbutton = Button('Quit',Rect(660,710,270,50),self.stop)

		# Widgets and focus route
		self.widgets = {
			self.addressfield: self.portfield,
			self.portfield: self.hostbutton,
			self.errorlabel: None,
			self.hostbutton: self.joinbutton,
			self.joinbutton: self.quitbutton,
			self.quitbutton: self.addressfield
		}

		self.focus(self.addressfield)

	def start(self):
		self.looping.start(1./self.targetfps)

	def stop(self, newscreen=None):
		self.looping.stop()

		if newscreen:
			newscreen.start()
		else: reactor.stop()

	def tick(self):
		# Handle events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.stop()
			elif event.type == pygame.KEYDOWN:
				if event.unicode == '\x09':
					self.focus(self.widgets[self.focuswidget])
				else: self.focuswidget.sendKey(event.unicode)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				for widget in self.widgets:
					if widget.click(event.button,event.pos):
						self.focus(widget)

		# Tick-tock
		for widget in self.widgets:
			widget.tick()

		# Update the screen
		self.screen.fill(self.black)

		for widget in self.widgets:
			widget.draw(self.screen)

		pygame.display.flip()

	def focus(self, widget):
		self.focuswidget = widget

		for w in self.widgets:
			w.setFocus(w is widget)

	def host(self):
		port = int(self.portfield.getText())

		if port < 1 or port > 65535:
			self.errorlabel.setText('invalid port number')
		else: self.stop(Hoster(self.screen,port))

	def join(self):
		address = self.addressfield.getText()
		port = int(self.portfield.getText())

		if port < 1 or port > 65535:
			self.errorlabel.setText('invalid port number')
		else: self.stop(Joiner(self.screen,address,port))

