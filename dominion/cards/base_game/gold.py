from dominion.cards import TreasureCard


class Gold(TreasureCard):
    def __init__(self):
        super().__init__(name='Gold', cost=6, value=3)


GOLD = Gold()
