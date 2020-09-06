from dominion.cards import Card
from dominion.common import CardType


class Curse(Card):
    def __init__(self):
        super().__init__(name='Curse', kind=CardType.CURSE, cost=0)
        self.vp = -1


CURSE = Curse()
