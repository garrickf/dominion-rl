from dominion.cards import TreasureCard


class Copper(TreasureCard):
    def __init__(self):
        super().__init__(name='Copper', cost=0, value=1)


COPPER = Copper()
