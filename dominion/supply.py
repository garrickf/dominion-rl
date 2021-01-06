""" The supply represents the collection of cards available for purchase during
the game.
"""

# Python stdlib
from collections import OrderedDict
from typing import List, MutableMapping, Sequence, Union

import numpy as np

# From dominion module
from dominion.common import DeckPile

from .cards import Card
from .cards.base_game import *


class Supply:
    def __init__(
        self, n_players: int = 2, debug: bool = False, cards: Sequence[Card] = None
    ) -> None:
        """Creates the supply. The rules for the initial supply are as follows:
        - All treasure cards are included. Each player starts with 7 coppers,
          taken from the supply.
        - 10 curses are included for a 2-player game, 20 for a 3-player game, and
          so on
        - For a two-player game, 8 of each victory card is placed in the supply.
          For three or four players, 12. The three Estates players start with
          come from the remainder in the box, *not* the supply.

        Args:
            n_players (int): The number of players in the game.
            debug (bool): If True, puts all the cards in the supply.
            cards (Sequence[Card]): Optional override to determine the 10 kingdom
                cards
        """
        # Choose 10 cards without replacement from set of all kingdom cards
        kingdom: List[Card] = np.random.choice(KINGDOM_CARDS, size=10, replace=False)

        if debug:
            kingdom = KINGDOM_CARDS
        if cards:
            kingdom = list(cards)

        self.kingdom = kingdom

        # Use an OrderedDict to allow indexing with a number
        self.supply_piles: MutableMapping[Card, int] = OrderedDict(
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
            self.supply_piles[card] = 10

    """ If the supply is indexed, iterated over, or its items retrieved,
    defer to the self.supply_piles object inside. Presents an abstraction wrapper
    w/o subclassing.
    """

    def items(self):
        return self.supply_piles.items()

    def values(self):
        return self.supply_piles.values()

    def __iter__(self):
        return self.supply_piles.__iter__()

    def __getitem__(self, index):
        return self.supply_piles.__getitem__(index)

    def buy(
        self,
        target: Union[int, Card],
        buyer,
        free: bool = False,
        to_pile: DeckPile = DeckPile.DISCARD,
    ) -> Card:
        """Buys and transfers card to buyer. If free=False, modifies the player
        object with the amount the player has spent so far. Does no error checking
        for the amount of treasures the player posesses.

        Args:
            target (int|Card): Index of which card, or the card, to buy
            buyer (Dominion.players.Player): Player object to transfer card to.
            free (bool, optional): Whether or not the transaction is free.
                Defaults to False.
            to_pile: (DeckPile): Which pile the purchased card should be placed in.
        """
        if isinstance(target, int):
            card = list(self.supply_piles.keys())[target]
        elif isinstance(target, Card):
            card = target
        else:
            raise TypeError(f"must be int or card, not {type(target).__name__}")

        self.supply_piles[card] -= 1
        buyer.deck.add([card], to_pile=to_pile)

        if free:
            return card

        if "spent" not in buyer.modifiers:
            buyer.modifiers["spent"] = 0
        buyer.modifiers["spent"] += card.cost
        return card
