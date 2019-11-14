from deck import Deck
from card import CARD_TYPES, AGENT_TYPES, PHASE_TYPES, ESTATE, DUTCHY, PROVINCE, CURSE
from util import get_integer

NUM_TO_DRAW = 7

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

        self.num_actions = 1
        self.num_buys = 1
        self.extra_treasure = 0


    def display_hand(self):
        s = 'Current hand:\n'
        for idx, card in enumerate(self.hand):
            s += '{}. {}\n'.format(idx, card)
        print(s)


    def display_state(self):
        print(self.deck)


    @property
    def can_play_action(self):
        for card in self.hand:
            if card.type == CARD_TYPES.ACTION:
                return True
        return False


    @property
    def name(self):
        return 'Player {} ({})'.format(self.player_number, 'Human') # TODO: add (Computer)


    @property
    def purchasing_power(self):
        total = 0
        for card in self.hand:
            if card.type == CARD_TYPES.TREASURE:
                total += card.treasure_value
        return total


    def action_phase(self, table):
        """
        During the action phase, a player can play any action card from their
        hand.
        """
        self.display_hand()

        action_cache = []
        while self.num_actions:
            if not self.can_play_action:
                print('No actions to play.\n')
                break

            print('{} action(s) left.'.format(self.num_actions))
            print('Play an action (0-{}) or ENTER to skip'.format(len(self.hand)-1))
            action = get_integer('? ') # TODO: out of bounds error checking is needed here
            if action == None:
                break
            
            while not self.hand[action].type == CARD_TYPES.ACTION:
                print('Not an action, try again!')
                print('Play an action (0-{}) or ENTER to skip'.format(len(self.hand)-1))
                action = get_integer("? ")
                if action == None:
                    # TODO: decompose better, the logic here isn't nice
                    self.num_actions = 1
                    return

            card = self.hand.pop(action)
            self.deck.discard([card]) # Place into discard
            card.action(self, AGENT_TYPES.SELF, PHASE_TYPES.IMMEDIATE, table)
            
            if card.action.affects_others:
                action_cache.append(card.action)

            self.num_actions -= 1
            self.display_hand()

        # Reset
        self.num_actions = 1
        return action_cache


    def buy_phase(self, table):
        pp = self.purchasing_power + self.extra_treasure
        extra = ' + extra' if self.extra_treasure else ''
        while self.num_buys:
            print('Value of treasures{}: {}, buys remaining: {}'.format(extra, pp, self.num_buys))
            print('On the table for purchase:')
            print(table)

            # Prompt
            print('Make a purchase or ENTER to skip')
            choice = get_integer("? ")
            if choice == None:
                break
            
            while not table.can_purchase(choice, pp):
                print('Can\'t buy that, try again!')
                print('Make a purchase or ENTER to skip')
                choice = get_integer("? ")
                if choice == None:
                    self.num_buys = 1
                    return

            # Buy card and update pp
            card = table.buy_idx(choice)
            pp -= card.cost
            self.num_buys -= 1
            self.deck.add_new(card)

        # Reset
        self.extra_treasure = 0
        self.num_buys = 1


    def cleanup_hand(self):
        self.deck.discard(self.hand)


    def draw_cards(self):
        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand = new_hand


    def compute_score(self):
        """
        Using the deck's card counts, calculate the number of victory points
        the player has.
        """
        return self.deck.counts[ESTATE] * 1 \
            + self.deck.counts[DUTCHY] * 3 \
            + self.deck.counts[PROVINCE] * 6 \
            + self.deck.counts[CURSE] * -1
        # TODO: include garden
