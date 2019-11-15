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


    @property
    def size(self):
        return sum([v for v in self.counts.values()])

    
    @property
    def discard_pile_size(self):
        return len(self.discard_pile)


    @property
    def draw_pile_size(self):
        return len(self.draw_pile)


    def reshuffle(self):
        random.shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []


    def draw(self, n):
        # If draw pile is smaller than n, reshuffle
        if len(self.draw_pile) < n: 
            self.reshuffle()

        drawn = self.draw_pile[:n]
        self.draw_pile = self.draw_pile[n:]
        return drawn


    def discard(self, cards):
        self.discard_pile += cards


    def push(self, card):
        self.draw_pile = [card] + self.draw_pile


    def add_new(self, card):
        self.discard_pile.append(card)
        self.counts[card] += 1


    def count(self, card):
        self.counts[card] += 1


    def trash(self, card):
        self.counts[card] -= 1


    def __str__(self):
        s = "Deck:\n"
        for k, v in self.counts.items():
            s += '{}: {}, '.format(k, v)
        return s[:-2] + '\n'
