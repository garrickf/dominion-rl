from enum import Enum

"""
Define the card class.
"""

class Card:
    """
    A card critically has a name, cost, and starting deck size.
    """
    def __init__(self, name, kind, cost, init_size, action=None):
        self.name = name
        self.type = kind
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
        return 'Card[{}]'.format(self.name)

# Create an enum of card types
CARD_TYPES = Enum('CARD_TYPES', 'VICTORY TREASURE ACTION CURSE')

"""
Victory cards
"""
PROVINCE = Card('Province', CARD_TYPES.VICTORY, 8, 8)
PROVINCE.set_victory_points(6)

DUTCHY = Card('Dutchy', CARD_TYPES.VICTORY, 5, 8)
DUTCHY.set_victory_points(3)

ESTATE = Card('Estate', CARD_TYPES.VICTORY, 2, 8)
ESTATE.set_victory_points(1)

"""
Treasure cards
"""
GOLD = Card('Gold', CARD_TYPES.TREASURE, 6, 30)
GOLD.set_treasure_value(3)

SILVER = Card('Silver', CARD_TYPES.TREASURE, 3, 40)
SILVER.set_treasure_value(2)

# Note: card numbers specific to a two player game
COPPER = Card('Copper', CARD_TYPES.TREASURE, 0, 46)
COPPER.set_treasure_value(1)