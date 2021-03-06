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
	BACKGROUND = pygame.image.load('WALLP2.png')

	def __init__(self, screen):
		self.screen = screen

		self.stopped = False
		self.targetfps = 60
		self.black = 0, 0, 0

		self.musicenabled = True

		self.looping = LoopingCall(self.tick)

		# Network config input fields
		self.addressfield = InputField('Server Address:',Rect(235,540,500,25),text='localhost')
		self.portfield = InputField('Server Port:',Rect(235,570,500,25),text='40100',numeric=True)
		self.errorlabel = TextLabel('',(235, 600),25,fgcolor=(255, 0, 0))

		# Enable/disable the background music
		self.musicbutton = Button('Music Enabled',Rect(335,630,300,40),self.toggleMusic)

		# Start a game or quit
		self.hostbutton = Button('Host a Game',Rect(40,710,270,50),self.host)
		self.joinbutton = Button('Join a Game',Rect(350,710,270,50),self.join)
		self.quitbutton = Button('Quit',Rect(660,710,270,50),self.stop)

		# Widgets and focus route (for tabbing through the elements)
		self.widgets = {
			self.addressfield: self.portfield,
			self.portfield: self.musicbutton,
			self.errorlabel: None,
			self.musicbutton: self.hostbutton,
			self.hostbutton: self.joinbutton,
			self.joinbutton: self.quitbutton,
			self.quitbutton: self.addressfield
		}

		self.focus(self.addressfield)

	# Call our tick function for each frame
	def start(self):
		self.looping.start(1./self.targetfps)

		# Start up the background music
		pygame.mixer.music.load('sounds/song_1.ogg')
		pygame.mixer.music.play(-1)

	# Stop calling our tick function, and activate the next screen, if there is one
	def stop(self, newscreen=None):
		self.looping.stop()

		self.stopped = True

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

		# Are we done, yet?
		if self.stopped: return

		# Update the screen
		self.screen.fill(self.black)

		self.screen.blit(MainScreen.BACKGROUND,(0, 0))

		for widget in self.widgets:
			widget.draw(self.screen)

		pygame.display.flip()

	def focus(self, widget):
		self.focuswidget = widget

		for w in self.widgets:
			w.setFocus(w is widget)

	# Turn the background music on or off
	def toggleMusic(self):
		self.musicenabled = not self.musicenabled

		if self.musicenabled:
			pygame.mixer.music.play(-1)
			self.musicbutton.setText('Music Enabled')
		else:
			pygame.mixer.music.stop()
			self.musicbutton.setText('Music Disabled')

	# Start up a game on the given port (ignore the address)
	def host(self):
		port = int(self.portfield.getText())

		if port < 1 or port > 65535:
			self.errorlabel.setText('invalid port number')
		else: self.stop(Hoster(self.screen,port))

	# Attempt to connect to the given address on the given port and join a game
	def join(self):
		address = self.addressfield.getText()
		port = int(self.portfield.getText())

		if port < 1 or port > 65535:
			self.errorlabel.setText('invalid port number')
		else: self.stop(Joiner(self.screen,address,port))

