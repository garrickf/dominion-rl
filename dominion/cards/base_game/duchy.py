from dominion.cards import VictoryCard


class Duchy(VictoryCard):
    def __init__(self):
        super().__init__(name="Duchy", cost=5, vp=3)


DUCHY = Duchy()
