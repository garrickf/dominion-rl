from card import *
from collections import OrderedDict as ordereddict
import numpy as np

np.random.seed(1)

# Flip to True to test all cards.
DEBUG = False

class Table:
    def __init__(self, num_players):
        """
        A table is a collection of card piles.
        """

        # Choose 10 cards without replacement from set of all kingdom cards
        kingdom = np.random.choice(KINGDOM_CARDS, size=10, replace=False)

        if DEBUG:
            kingdom = KINGDOM_CARDS

        self.kingdom = kingdom
        
        # Use a ordered dict to allow indexing with a number
        self.table = ordereddict({
            COPPER: 60 - (num_players * 7),
            SILVER: 40,
            GOLD: 30,
            ESTATE: 8 if num_players == 2 else 12,
            DUTCHY: 8 if num_players == 2 else 12,
            PROVINCE: 8 if num_players == 2 else 12,
            CURSE: 10 * (num_players - 1),
        })

        for card in kingdom:
            self.table[card] = 10


    def __str__(self):
        """
        Returns a string representation of the table.
        """
        s = '{:<4}{:<14}{:<5}{:<7}{:<}\n'.format('', 'Name', 'Left', 'Cost', 'Description')
        for i, (card, left) in enumerate(self.table.items()):
            s += '{:>2}. {!s:<23} [{:>2}] ({:>2}) | {}\n'.format(i, card, left, card.cost, card.description)
        return s


    @property
    def cards(self):
        """
        Returns the list of cards on the table.
        """
        return list(self.table.keys())


    @property
    def num_empty_piles(self):
        """
        Returns the number of empty piles
        """
        empty_piles = [v for v in self.table.values() if v == 0]
        return len(empty_piles)


    def can_purchase(self, idx, treasures, card_type_only=None):
        """
        A card is available for purcase if there is more in the pile, and the
        cost is at most the amount of treasures available.
        """
        card, left = list(self.table.items())[idx]
        if card_type_only and card.type != card_type_only:
            return False

        return card.cost <= treasures and left >= 1


    def can_purchase_card(self, card, worth):
        """
        A card is available for purcase if there is more in the pile, and the
        cost is at most the amount of treasures available.
        """
        left = self.table[card]
        return card.cost <= worth and left >= 1


    def get_purchasable_cards(self, worth, card_type_only=None):
        """
        Return the set of cards available for purchase as a list of indexes.
        """
        purchasable = []
        for idx, (card, left) in enumerate(list(self.table.items())):
            if card_type_only and card.type != card_type_only:
                continue
            if card.cost <= worth and left >= 1:
                purchasable.append(idx)
        return purchasable


    def buy_idx(self, idx):
        """
        When passed an index of a card, perform a purchase of the card, removing
        one count of it from the table and returning a shared instance of it to
        the player.
        """
        card, _ = list(self.table.items())[idx]
        self.table[card] -= 1
        return card


    def get_card(self, card):
        """
        If a specific card is desired, just pull one of it from the table. If there
        are no cards left in the pile, returns False.
        """
        if self.table[card] >= 1:
            self.table[card] -= 1
            return True
        return False
        


    def reached_end(self):
        """
        Returns true if the end of the game is reached. This can happen when:
        - There are no more provinces
        - 3 piles are empty (4 in a four player game)
        """
        if self.table[PROVINCE] == 0:
            return True

        n_piles_empty = len([v for v in self.table.values() if v == 0])
        if n_piles_empty >= 3:
            return True

        return False
