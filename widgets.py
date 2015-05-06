#
# UI widget classes.
#

import pygame
import re

from pygame.rect import Rect

# Basic superclass; mostly skeleton code
class Widget:
	def __init__(self, rect):
		self.rect = rect

		self.focus = False

	def setFocus(self, focus):
		self.focus = focus

	def setRect(self, rect):
		self.rect = rect

	def click(self, button, position):
		return self.rect.collidepoint(position)

	def sendKey(self, key):
		pass

	def tick(self):
		pass

	def draw(self, screen):
		pass

# Button with a text label; invokes a callback when clicked on by the mouse, or
# when the enter key is pressed while in focus.
class Button(Widget):
	def __init__(self, text, rect, callback, fgcolor=(255, 255, 255)):
		Widget.__init__(self,rect)

		self.fgcolor = fgcolor
		self.callback = callback

		textscale = 0.8
		self.font = pygame.font.Font(None,int(textscale*rect.h))
		self.setText(text)

	def setText(self, text):
		self.textsurf = self.font.render(text,True,self.fgcolor)

	def click(self, button, position):
		if button == 1 and self.rect.collidepoint(position):
			self.callback()
			return True
		else: return False

	def sendKey(self, key):
		if key == '\x0d': # Enter key
			self.callback()

	def draw(self, screen):
		# Outline
		thickness = 4 if self.focus else 2
		pygame.draw.rect(screen,self.fgcolor,self.rect,thickness)

		# Text label
		textposition = (self.rect.x + (self.rect.w - self.textsurf.get_width())/2,
			self.rect.y + (self.rect.h - self.textsurf.get_height())/2)
		screen.blit(self.textsurf,textposition)

# Simple, single-line text display
class TextLabel(Widget):
	def __init__(self, text, position, size, fgcolor=(255, 255, 255)):
		Widget.__init__(self,Rect(position,(0, 0)))

		self.position = position
		self.fgcolor = fgcolor

		self.font = pygame.font.Font(None,size)

		self.setText(text)

	def setText(self, text):
		self.textsurf = self.font.render(text,True,self.fgcolor)

		self.setRect(Rect(self.position,self.textsurf.get_size()))

	def draw(self, screen):
		screen.blit(self.textsurf,self.position)

# Single-line textual input, with a text label on the left
class InputField(Widget):
	def __init__(self, labeltext, rect, text='', numeric=False, fgcolor=(255, 255, 255)):
		Widget.__init__(self,rect)

		self.numeric = numeric
		self.fgcolor = fgcolor

		self.font = pygame.font.Font(None,rect.h)
		self.labelsurf = self.font.render(labeltext,True,self.fgcolor)

		self.setText(text)

	# Get the input contents
	def getText(self):
		if self.numeric and len(self.text) == 0:
			return '0'
		else: return self.text

	# Update the input contents
	def setText(self, text):
		if self.numeric:
			self.text = re.sub('[^0-9]','',text)
		else: self.text = text

		self.textsurf = self.font.render(self.text,True,self.fgcolor)

	def sendKey(self, key):
		if key == '\x08': # Backspace
			self.setText(self.text[:-1])
		else: self.setText(self.text + key.encode('utf-8')) # Add to contents

	def draw(self, screen):
		# Label
		screen.blit(self.labelsurf,self.rect.topleft)

		# Current input
		labelgap = 5
		textposition = (self.rect.x + self.labelsurf.get_width() + labelgap, self.rect.y)
		screen.blit(self.textsurf,textposition)

		# Underline
		underliney = textposition[1] + self.textsurf.get_height()
		pygame.draw.line(screen,self.fgcolor,(textposition[0], underliney),(self.rect.right, underliney))

		# Blinking cursor
		blinkperiod = 500
		if self.focus and pygame.time.get_ticks()/blinkperiod%2:
			cursor = Rect((textposition[0] + self.textsurf.get_width(), self.rect.y),
				(1, self.textsurf.get_height()))
			screen.fill(self.fgcolor,rect=cursor)

