""" Player objects TODO: add docstring
"""

from abc import ABC, abstractmethod
import random  # For shuffle
from collections import defaultdict
from dominion.cards.base_game import ESTATE, COPPER
from dominion.common import DeckPile, PlayerType, CardType
from dominion.controller import Controller

STARTER_DECK = [ESTATE] * 3 + [COPPER] * 7


class Deck:
    def __init__(self, starter_deck=STARTER_DECK):
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


class Player(ABC):
    def __init__(self, name):
        self.name = name
        self.deck = Deck()
        self.modifiers = {}

    @property
    def hand(self):
        """ Shorthand property for the player's hand."""
        return self.deck.hand

    @property
    def treasure(self):
        """ How much treasure the player has on hand."""
        total = 0
        for card in self.hand:
            if card.kind == CardType.TREASURE:
                total += card.value

        # TODO: account for boons

        if 'spent' in self.modifiers:
            total -= self.modifiers['spent']

        return total

    def reset_modifiers(self):
        self.modifiers = {}

    @abstractmethod
    def get_input(self, prompt, options, allow_skip=False):
        pass


class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.type = PlayerType.HUMAN
        self.controller = Controller()

    def get_input(self, prompt, options, allow_skip=False):
        """
        @param options (dict): Number -> String option
        """
        return self.controller.get_input(prompt,
                                         options,
                                         allow_skip=allow_skip)

    def show(self, text):
        print(text)


# Need to subclass the ComputerPlayer with an appropriate learn method and policy
class ComputerPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.type = PlayerType.COMPUTER

    @abstractmethod
    def reflect(self):
        pass


def get_playable_actions_as_options(cards):
    """ Takes a list of cards and returns a dict from index to string option
    """
    options = {}
    for idx, card in enumerate(cards):
        if card.kind == CardType.ACTION:
            options[idx] = card.name
    return options


def get_purchasable_cards_as_options(table, player):
    options = {}
    for idx, card in enumerate(table):
        left = table[card]
        if card.cost <= player.treasure and left > 0:
            options[idx] = card.name
    return options
