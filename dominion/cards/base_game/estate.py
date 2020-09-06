from dominion.cards import VictoryCard


class Estate(VictoryCard):
    def __init__(self):
        super().__init__(name='Estate', cost=2, vp=1)


ESTATE = Estate()
