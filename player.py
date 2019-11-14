from hand import Hand
from deck import Deck

NUM_TO_DRAW = 7

class Player:
    def __init__(self, i):
        """
        Every player has an active Hand and a Deck, divided between a draw pile
        and a discard pile.
        """
        self.player_number = i
        self.hand = Hand()
        self.deck = Deck()

        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand.replenish(new_hand)

    def display_hand(self):
        print(self.hand)

    def action_phase(self):
        print("Play an action ideally")
        input("? ")
        # TODO: do the action

    def buy_phase(self, table):
        print("Play an buy ideally")
        input("? ")
        # TODO: set number of buys and actions

    def cleanup_hand(self):
        self.deck.discard(self.hand.get_hand())

    def draw_cards(self):
        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand.replenish(new_hand)

    def compute_score(self):
        return 0