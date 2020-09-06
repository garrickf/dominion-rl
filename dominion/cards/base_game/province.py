from dominion.cards import VictoryCard


class Province(VictoryCard):
    def __init__(self):
        super().__init__(name='Province', cost=8, vp=6)


PROVINCE = Province()
