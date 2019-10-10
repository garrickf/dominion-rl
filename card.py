"""
Define the card class.
"""

class Card:
	"""
	A card critically has a name, cost, and starting deck size.
	"""
	def __init__(self, name, cost, init_size, action=None):
		self.name = name
		self.cost = cost
		self.init_size = init_size
		self.action = action
		# TODO: add description, type, flesh out how action works

	def set_victory_points(self, points):
		self.victory_points = points

	def set_treasure_value(self, value):
		self.treasure_value = value

	"""
	Prints a string represenation of the card; useful during gameplay.
	"""
	def __str__(self):
		return 'Card["' + self.name + '"]'

"""
Victory cards
"""
PROVINCE = Card('Province', 8, 8)
PROVINCE.set_victory_points(6)

DUTCHY = Card('Dutchy', 5, 8)
DUTCHY.set_victory_points(3)

ESTATE = Card('Estate', 2, 8)
ESTATE.set_victory_points(1)

"""
Treasure cards
"""
GOLD = Card('Gold', 6, 30)
GOLD.set_treasure_value(3)

SILVER = Card('Silver', 3, 40)
SILVER.set_treasure_value(2)

# Note: card numbers specific to a two player game
COPPER = Card('Copper', 0, 46)
COPPER.set_treasure_value(1)