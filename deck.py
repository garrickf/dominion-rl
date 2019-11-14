from card import Card, ESTATE, COPPER
import random # For shuffle

"""
The deck implements a discard pile/draw pile with shuffle and reshuffle.
Currently assumes a two player game
"""

class Deck:
    """
    Every player starts off with 3 Estates and 7 Coppers.
    """
    def __init__(self):
        self.draw_pile = [ESTATE] * 3 + [COPPER] * 7
        random.shuffle(self.draw_pile)
        self.discard_pile = []

    def reshuffle(self):
        random.shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []

    def draw(self, n):
        print(self)
        # If draw pile is smaller than n, reshuffle
        if len(self.draw_pile) < n: 
            self.reshuffle()

        drawn = self.draw_pile[:n]
        self.draw_pile = self.draw_pile[n:]
        return drawn

    def discard(self, cards):
        self.discard_pile += cards

    def __str__(self):
        s = ""
        for card in self.draw_pile:
            s += str(card) + '\n'
        return s
