from dominion.cards import VictoryCard


class Gardens(VictoryCard):
    def __init__(self):
        super().__init__(name='Gardens',
                         cost=4,
                         vp=0,
                         desc='Worth 1 VP per 10 cards you have (round down).')


GARDENS = Gardens()
