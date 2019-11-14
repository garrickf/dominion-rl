from card import Card, ESTATE, COPPER
import random # For shuffle
from collections import defaultdict

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

        self.counts = defaultdict(int, {ESTATE: 3, COPPER: 7})


    def reshuffle(self):
        random.shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []

        num_cards = sum([v for v in self.counts.values()])
        assert(len(self.draw_pile) == num_cards)


    def draw(self, n):
        # If draw pile is smaller than n, reshuffle
        if len(self.draw_pile) < n: 
            self.reshuffle()

        drawn = self.draw_pile[:n]
        self.draw_pile = self.draw_pile[n:]
        return drawn


    def discard(self, cards):
        self.discard_pile += cards


    def add_new(self, card):
        self.discard_pile.append(card)
        self.counts[card] += 1


    def trash(self, card):
        self.counts[card] -= 1


    def __str__(self):
        s = "Deck:\n"
        for k, v in self.counts.items():
            s += '{}: {}\n'.format(k, v)
        return s
