from card import Card

"""
A store of cards controls the interactions over when cards are bought.
"""

# TODO: shift numleft here?
class Store:
    def __init__(self, card):
        self.card = card
        self.num_left = card.init_size
        self.cost = card.cost

    """
    Returns an instance of the card from the store.
    """
    def buy(self):
        self.num_left -= 1
        return self.card

    """
    Returns whether or not a card can be bought from this store.
    """
    def can_buy(self, treasures, num_buys):
        return treasures >= self.cost and num_buys > 0

    def __str__(self):
        return 'Store[' + str(self.card) + ',\t cost: ' + str(self.cost) + ', num_left: ' + str(self.num_left) + '\t]'
