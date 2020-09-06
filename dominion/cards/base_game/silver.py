from dominion.cards import TreasureCard


class Silver(TreasureCard):
    def __init__(self):
        super().__init__(name='Silver', cost=3, value=2)


SILVER = Silver()
