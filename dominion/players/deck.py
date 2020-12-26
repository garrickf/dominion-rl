""" Deck TODO: docstring
"""

import random  # For shuffle
from collections import defaultdict
from dominion.common import DeckPile
from dominion.cards.base_game import STARTER_DECK
from dominion.cards import Card


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
        """Helper method that shuffles the discard pile back into the draw
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

    def draw_cards(self, n=1, replace_hand=True, to_caller=False):
        """Draw n cards, optionally replacing (discarding) cards in hand. or 
        returning cards directly."""
        if not to_caller and replace_hand:
            self._discard(self.hand)
            self.hand = []

        # If draw pile is smaller than n, reshuffle
        if len(self.draw_pile) < n:
            self._reshuffle()

        drawn = self.draw_pile[:n]
        self.draw_pile = self.draw_pile[n:]

        # Return cards to caller if specified; otherwise, add to hand
        if to_caller:
            return drawn

        self.hand += drawn
        return self.hand

    def trash(self, cards, from_pile=DeckPile.HAND):
        """Remove a list of cards from a specified pile. Reduces overall deck
        counts.
        """
        if from_pile == DeckPile.HAND:
            for card in cards:
                self.hand.remove(card)
        elif isinstance(from_pile, DeckPile):
            raise NotImplementedError("Not implemented")
        else:
            raise ValueError("from_pile not of type DeckPile")
        self._update_counts()

    def add(self, cards, to_pile=DeckPile.DISCARD):
        """Add list of cards to a specified pile. Increases overall deck
        counts.
        """
        if to_pile == DeckPile.DISCARD:
            self.discard_pile += cards
        elif to_pile == DeckPile.HAND:
            self.hand += cards
        elif to_pile == DeckPile.DRAW:
            # Add to top of draw pile
            self.draw_pile = cards + self.draw_pile
        elif isinstance(to_pile, DeckPile):
            raise NotImplementedError("Not implemented")
        else:
            raise ValueError("to_pile not of type DeckPile")
        self._update_counts()

    def move(self, targets, *, from_pile, to_pile, to_pos="TOP"):
        """Move list of cards from one pile to another. Preserves overall deck
        counts.
        """
        ENUM_TO_PILE = {
            DeckPile.DISCARD: self.discard_pile,
            DeckPile.DRAW: self.draw_pile,
            DeckPile.HAND: self.hand,
        }

        from_pile = ENUM_TO_PILE[from_pile]
        to_pile = ENUM_TO_PILE[to_pile]

        if type(targets) is not list:
            targets = [targets]

        if isinstance(targets[0], int):
            target_idxs = targets
        elif isinstance(targets[0], Card):
            target_idxs = []
            for idx, card in enumerate(from_pile):
                if card in targets:
                    target_idxs.append(idx)
                    targets.remove(card)

            if targets:
                raise RuntimeError("Desired card not found in from_pile")
        else:
            raise RuntimeError(
                f"target should be int or card, got {type(targets[0]).__name__}"
            )

        new_from_pile = []
        moved = []
        for idx, card in enumerate(from_pile):
            if idx in target_idxs:
                moved.append(card)
            else:
                new_from_pile.append(card)

        # Change internal contents, not switch views
        from_pile[:] = new_from_pile

        if to_pos == "TOP":
            to_pile[:] = to_pile + moved
        elif to_pos == "BOTTOM":
            to_pile[:] = moved + to_pile
        else:
            raise NotImplementedError("Not implemented")
