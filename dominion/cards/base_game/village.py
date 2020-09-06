from dominion.cards import ActionCard

class Village(ActionCard):
    def __init__(self):
        super().__init__(name='Village', cost=2, desc='+1 card. +2 actions.')

    def play(self, by, game_ctx):
        pass

VILLAGE = Village()
