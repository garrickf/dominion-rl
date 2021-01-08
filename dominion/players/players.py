"""Player objects contain player metadata and convenience methods for other
classes to manipulate that data.
"""

# Python stdlib
from abc import ABC, abstractmethod
from math import floor

# From dominion module
import dominion.util.logging as logging
from dominion.cards.base_game import CURSE, DUCHY, ESTATE, GARDENS, PROVINCE
from dominion.common import CardType, PlayerType
from dominion.controller import Controller
from dominion.policy import Policy

from .deck import Deck


class Player(ABC):
    def __init__(self, name: str) -> None:
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

    def cleanup(self):
        # Reset modifiers
        self.modifiers = {}

        # Move played cards to discard
        self.deck.cleanup()

    def set_modifier(self, key, func, default=0):
        if key not in self.modifiers:
            self.modifiers[key] = default

        self.modifiers[key] = func(self.modifiers[key])

    @abstractmethod
    def get_input(self, prompt, options, allow_skip=False):
        """Each Player subclass must implement this method, which prompts
        the player to take an action.
        """
        pass

    @abstractmethod
    def show(self, text):
        """Each Player subclass must implement this method, which shows the
        player information on the moves they are able to make.
        """
        pass

    def compute_score(self) -> int:
        """Using the deck's card counts, calculate the number of victory points
        the player has.
        """
        return (
            self.deck.counts[ESTATE] * 1
            + self.deck.counts[DUCHY] * 3
            + self.deck.counts[PROVINCE] * 6
            + self.deck.counts[CURSE] * -1
            + self.deck.counts[GARDENS] * floor(len(self.deck) / 10)
        )


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
        logging.log(self.name, text)


class ComputerPlayer(Player):
    def __init__(self, name: str, policy: Policy) -> None:
        super().__init__(name)
        self.type = PlayerType.COMPUTER
        self.policy = policy

    def get_input(self, _, options, allow_skip: bool = False):
        # Consult the policy on what the action should be
        return self.policy.get_input(options, allow_skip=allow_skip)

    def show(self, text):
        logging.log(self.name, text)
