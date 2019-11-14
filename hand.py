"""
The hand represents a player's that they can view and act with.
"""

class Hand:
    def __init__(self):
        self.hand = []

    def pop(self, idx):
        return self.hand.pop(idx)

    def append(self, new_card):
        self.hand.append(new_card)

    def get_hand(self):
        return self.hand

    def replenish(self, new_hand):
        """
        Replaces the hand with a new array of cards.
        """
        self.hand = new_hand

    def __str__(self):
        s = ""
        for idx, card in enumerate(self.hand):
            s += '{}. {}\n'.format(idx, card)
        return s