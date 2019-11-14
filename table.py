from card import *
from collections import OrderedDict as ordereddict

class Table:
    def __init__(self):
        """
        A table is a collection of card piles
        """

        # NOTE: for 3-4 players, 12 each of victory cards
        # 10 Kingdom cards
        # 10 curse cards for each player beyond the first
        self.table = ordereddict({
            COPPER: 60 - (2 * 7),
            SILVER: 40,
            GOLD: 30,
            ESTATE: 8,
            DUTCHY: 8,
            PROVINCE: 8,
            CURSE: 10 * (2 - 1),
            # Kingdom (10)
            CHAPEL: 10,
            SMITHY: 10,
        })


    def __str__(self):
        s = '    Name\t Left\tCost\n'
        for i, (card, left) in enumerate(self.table.items()):
            s += '{:>2}. {}\t[{:>4}] {:>5} | {}\n'.format(i, card, left, card.cost, card.description)
        return s


    def can_purchase(self, idx, treasures):
        """
        A card is available for purcase if there is more in the pile, and the
        cost is at most the amount of treasures available.
        """
        card, left = list(self.table.items())[idx]
        return card.cost <= treasures and left > 1


    def buy(self, idx):
        card, _ = list(self.table.items())[idx]
        self.table[card] -= 1
        return card


    def reached_end(self):
        return False
