#
# This class is a wrapper for all of the variables for the
# game. Class is pickled and then sent and received over the 
# connection in order to communicate the game state
#
class Values():
	def __init__(self):

		#Card Dictionaries
		self.card_curFrame = dict()
		self.card_Flip = dict()
		self.card_flipDirection = dict()
		self.card_selected = dict()
		self.card_matched = dict()
		self.card_value = dict()

		#GS Values
		self.firstCard = 0
		self.message = ""
		self.p1 = 0
		self.p2 = 0
		self.turn = 1
		self.timer = 0
		self.startTimer = False

		#card values initiated
		for i in range(0,24):
			self.card_curFrame[i] = 0
			self.card_Flip[i] = False
			self.card_flipDirection[i] = 1
			self.card_selected[i] = False
			self.card_matched[i] = False
			self.card_value[i] = -1


	def save(self,gs):
		# Save all GS values
		self.firstCard = gs.firstCard
		self.message = gs.message
		self.p1 = gs.p1
		self.p2 = gs.p2
		self.turn = gs.turn
		self.timer = gs.timer
		self.startTimer = gs.startTimer

		# Save all card values
		for i in range(0,24):
			self.card_curFrame[i] = gs.card_list[i].curFrame
			self.card_Flip[i] = gs.card_list[i].Flip
			self.card_flipDirection[i] = gs.card_list[i].flipDirection
			self.card_selected[i] = gs.card_list[i].selected
			self.card_matched[i] = gs.card_list[i].matched
			self.card_value[i] = gs.card_list[i].value

