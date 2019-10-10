from card import Card, ESTATE, COPPER
import random # For shuffle

"""
The deck implements a discard pile/deck with shuffle and reshuffle
"""

class Deck:
	"""
	Every player starts off with 3 Estates and 7 Coppers.
	"""
	def __init__(self):
		self.deck = [ESTATE] * 3 + [COPPER] * 7
		self.shuffle()
		self.discard_pile = []

	def __str__(self):
		s = ""
		for card in self.deck:
			s += card.__str__() + '\n'
		return s

	def shuffle(self):
		random.shuffle(self.deck)

	def reshuffle(self):
		self.deck = self.discard_pile
		self.discard_pile = []
		shuffle()

	def draw(n):
		drawn = self.deck[:n]
		self.deck = self.deck[n:]
		return drawn
