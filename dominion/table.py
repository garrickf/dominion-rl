""" The table represents the collection of cards available for purchase during
the game.
"""

from collections import OrderedDict

import numpy as np

from dominion.common import DeckPile
from .cards.base_game import *
from .cards import Card

np.random.seed(1)

# Flip debug to True to test all cards.
DEBUG = True
FIXED = False


class Table:
    def __init__(self, n_players=2):
        # Choose 10 cards without replacement from set of all kingdom cards
        kingdom = np.random.choice(KINGDOM_CARDS, size=10, replace=False)

        if DEBUG:
            kingdom = KINGDOM_CARDS
        if FIXED:
            kingdom = [
                CHAPEL,
                BANDIT,
                WITCH,
                MARKET,
                VILLAGE,
                SMITHY,
                MINE,
                MERCHANT,
                WORKSHOP,
                CELLAR,
            ]

        self.kingdom = kingdom

        # Use an OrderedDict to allow indexing with a number
        self.table = OrderedDict(
            {
                COPPER: 60 - (n_players * 7),
                SILVER: 40,
                GOLD: 30,
                ESTATE: 8 if n_players == 2 else 12,
                DUCHY: 8 if n_players == 2 else 12,
                PROVINCE: 8 if n_players == 2 else 12,
                CURSE: 10 * (n_players - 1),
            }
        )

        for card in kingdom:
            self.table[card] = 10

    """ If the table is indexed, iterated over, or its items retrieved,
    defer to the self.table object inside. Presents an abstraction wrapper
    w/o subclassing.
    """

    def items(self):
        return self.table.items()

    def __iter__(self):
        return self.table.__iter__()

    def __getitem__(self, index):
        return self.table.__getitem__(index)

    def buy(self, target, buyer, free=False, to_pile=DeckPile.DISCARD):
        """Buys and transfers card to buyer. If free=False, modifies the player
        object with the amount the player has spent so far. Currently, does no
        error checking for the amount of treasures the player posesses.

        Args:
            idx (int): Index of which card to buy.
            buyer (Dominion.players.Player): Player object to transfer card to.
            free (bool, optional): Whether or not the transaction is free.
                Defaults to False.
        """
        if isinstance(target, int):
            card = list(self.table.keys())[target]
        elif isinstance(target, Card):
            card = target
        else:
            raise RuntimeError(f"target should be int or card, got {type(target).__name__}")

        self.table[card] -= 1
        buyer.deck.add([card], to_pile=to_pile)

        if free:
            return card

        if "spent" not in buyer.modifiers:
            buyer.modifiers["spent"] = 0
        buyer.modifiers["spent"] += card.cost
        return card
