""" Deck TODO: docstring
"""

import random  # For shuffle
from collections import defaultdict
from dominion.common import DeckPile
from dominion.cards.base_game import STARTER_DECK


class Deck:
    def __init__(self, *, starter_deck=STARTER_DECK):
        self.draw_pile = starter_deck
        random.shuffle(self.draw_pile)
        self.discard_pile = []
        self.hand = []
        self._update_counts()

    def __len__(self):
        return sum([v for v in self.counts.values()])

    def _reshuffle(self):
        """ Helper method that shuffles the discard pile back into the draw 
        pile.
        """
        random.shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []

    def _update_counts(self):
        self.counts = defaultdict(int)
        for card in self.draw_pile + self.discard_pile + self.hand:
            self.counts[card] += 1

    def _discard(self, cards):
        self.discard_pile += cards

    def draw_cards(self, n=1, replace_hand=True):
        """ Draw n cards, optionally replacing (discarding) cards in hand.
        """
        if replace_hand:
            self._discard(self.hand)
            self.hand = []

        # If draw pile is smaller than n, reshuffle
        if len(self.draw_pile) < n:
            self._reshuffle()

        self.hand += self.draw_pile[:n]
        self.draw_pile = self.draw_pile[n:]
        return self.hand

    def trash(self, cards, from_pile=DeckPile.HAND):
        """ Remove a list of cards from a specified pile. Reduces overall deck
        counts.
        """
        if from_pile == DeckPile.HAND:
            for card in cards:
                self.hand.remove(card)
        elif isinstance(from_pile, DeckPile):
            raise NotImplementedError('Not implemented')
        else:
            raise ValueError('from_pile not of type DeckPile')
        self._update_counts()

    def add(self, cards, to_pile=DeckPile.DISCARD):
        """ Add list of cards to a specified pile. Increases overall deck 
        counts.
        """
        if to_pile == DeckPile.DISCARD:
            self.discard_pile += cards
        elif isinstance(to_pile, DeckPile):
            raise NotImplementedError('Not implemented')
        else:
            raise ValueError('to_pile not of type DeckPile')
        self._update_counts()

    # TODO: for more precision, allow move by index
    def move(self, cards, *, from_pile, to_pile, to_pos='TOP'):
        """ Move list of cards from one pile to another. Preserves overall deck 
        counts. Only moves to the top of the destination pile.
        """
        if to_pos != 'TOP':
            raise NotImplementedError('Not implemented')

        ENUM_TO_PILE = {
            DeckPile.DISCARD: self.discard_pile,
            DeckPile.DRAW: self.draw_pile,
            DeckPile.HAND: self.hand,
        }

        from_pile = ENUM_TO_PILE[from_pile]
        to_pile = ENUM_TO_PILE[to_pile]

        for card in cards:
            if card not in from_pile:
                raise RuntimeError('Desired card not found in from_pile')
            from_pile.remove(card)
            to_pile.insert(0, card)

        # TODO: allow int indexing as well as passing a list of names