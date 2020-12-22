""" Player objects contain player metadata and convenience methods for other
classes to manipulate that data.
"""

from abc import ABC, abstractmethod

from dominion.common import CardType, PlayerType
from dominion.controller import Controller

from .deck import Deck


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

        if "extra_treasure" in self.modifiers:
            total += self.modifiers["extra_treasure"]

        if "spent" in self.modifiers:
            total -= self.modifiers["spent"]

        return total

    def reset_modifiers(self):
        self.modifiers = {}

    def set_modifier(self, key, func, default=0):
        if key not in self.modifiers:
            self.modifiers[key] = default

        self.modifiers[key] = func(self.modifiers[key])

    @abstractmethod
    def get_input(self, prompt, options, allow_skip=False):
        """ Each Player subclass must implement this method.
        """
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
        return self.controller.get_input(prompt, options, allow_skip=allow_skip)

    def show(self, text):
        # TODO: incorporate with logging: to player, and to display, but not to game
        print(text)


# Need to subclass the ComputerPlayer with an appropriate learn method and policy
class ComputerPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.type = PlayerType.COMPUTER

    @abstractmethod
    def reflect(self):
        pass
