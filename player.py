from deck import Deck
from card import CARD_TYPES, AGENT_TYPES, PHASE_TYPES

NUM_TO_DRAW = 7

def get_integer(prompt):
    typed = input(prompt)
    if typed.isdigit():
        return int(typed)
    elif typed == '':
        return None

class Player:
    def __init__(self, i):
        """
        Every player has an active Hand and a Deck, divided between a draw pile
        and a discard pile.
        """
        self.player_number = i
        self.hand = []
        self.deck = Deck()

        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand = new_hand


    def display_hand(self):
        s = 'Current hand:\n'
        for idx, card in enumerate(self.hand):
            s += '{}. {}\n'.format(idx, card)
        print(s)


    def display_state(self):
        print(self.deck)
        self.display_hand()


    @property
    def can_play_action(self):
        for card in self.hand:
            if card.type == CARD_TYPES.ACTION:
                return True
        return False


    @property
    def purchasing_power(self):
        total = 0
        for card in self.hand:
            if card.type == CARD_TYPES.TREASURE:
                total += card.treasure_value
        return total


    def action_phase(self):
        """
        During the action phase, a player can play any action card from their
        hand.
        """
        if not self.can_play_action:
            print('No actions to play.\n')
            return

        print('Play an action (0-{}) or ENTER to skip'.format(len(self.hand)-1))
        action = get_integer('? ')
        if action == None:
            return
        
        while not self.hand[action].type == CARD_TYPES.ACTION:
            print('Not an action, try again!')
            print('Play an action (0-{}) or ENTER to skip'.format(len(self.hand)-1))
            action = get_integer("? ")
            if action == None:
                return

        card = self.hand.pop(action)
        card.action(self, AGENT_TYPES.SELF, PHASE_TYPES.IMMEDIATE)
        if not card.action.affects_others:
            print('This action does not affect other players.')
        # TODO: pass action(s) to game object, so they can be applied to other players as effects


    def buy_phase(self, table):
        print('Total value of treasures: {}'.format(self.purchasing_power))
        print('On the table for purchase:')
        print(table)
        print('Make a purchase or ENTER to skip')
        choice = get_integer("? ")
        if choice == None:
            return
        
        while not table.can_purchase(choice, self.purchasing_power):
            print('Too expensive, try again!')
            print('Make a purchase or ENTER to skip')
            choice = get_integer("? ")
            if choice == None:
                return

        card = table.buy(choice)
        self.deck.add_new(card)


    # TODO: could just represent the hand as an array
    def cleanup_hand(self):
        self.deck.discard(self.hand)


    def draw_cards(self):
        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand = new_hand


    def compute_score(self):
        return 0
