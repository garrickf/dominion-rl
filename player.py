from math import floor
from deck import Deck
from card import CARD_TYPES, AGENT_TYPES, PHASE_TYPES, ESTATE, DUTCHY, PROVINCE, CURSE, GARDENS
from util import get_integer, get_choice

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
        self.throne_room_action = None # It's that special


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


    @property
    def valid_actions(self):
        """
        Returns a list of valid actions. No action is always valid, though frowned
        upon.
        """
        return [idx for idx, card in enumerate(self.hand) if card.type == CARD_TYPES.ACTION] + [None]


    def execute_action(self, action, phase, table, self_initiated=False):
        """
        Given some action and table, run the action to completion. Some actions 
        only induce effects on the Player object; others prompt the player to do
        something in other to complete the action.
        """
        if self_initiated:
            agent_type = AGENT_TYPES.SELF
        else:
            agent_type = AGENT_TYPES.OTHER
        
        g = action(self, agent_type, phase, table)
        if g != None:
            # The generator must be called once to start the action
            try:
                choices, prompt_str = next(g)
                while True:
                    """
                    The action generator returns a set of valid choices. From
                    those, we prompt the player to enter one, and pass the
                    choice back to the generator.
                    """
                    choice = get_choice(prompt_str, choice_set=choices)
                    choices, prompt_str = g.send(choice)
            except:
                pass


    def action_phase(self, table):
        """
        During the action phase, a player can play any action card from their
        hand.
        """
        self.display_hand()

        # Cache actions to be applied to other players and self
        other_cache = []
        self_cache = []
        while self.num_actions:
            if not self.can_play_action:
                print('No actions to play.\n')
                break

            print('{} action(s) left.'.format(self.num_actions))
            prompt_str = 'Play an action (0-{}) or ENTER to skip'.format(len(self.hand)-1)
            action_idx = get_choice(prompt_str, choice_set=self.valid_actions)
            if action_idx == None:
                break

            card = self.hand.pop(action_idx)
            print('{} played {}\n'.format(self.name, card))
            self.deck.discard([card]) # Place into discard

            # Execute the action
            action = card.action
            self.execute_action(action, PHASE_TYPES.IMMEDIATE, table, self_initiated=True)
            
            if action.affects_others:
                other_cache.append(action)
            self_cache.append(action)

            if self.throne_room_action:
                for i in range(2):
                    self.execute_action(self.throne_room_action, PHASE_TYPES.IMMEDIATE, table, self_initiated=True)
                    if self.throne_room_action.affects_others:
                        other_cache.append(self.throne_room_action)
                    self_cache.append(self.throne_room_action)

            self.num_actions -= 1
            self.display_hand()
        print('{} concludes action phase\n'.format(self.name))

        # Debug: Cards should not disappear without our consent
        assert(self.deck.size == self.deck.draw_pile_size + self.deck.discard_pile_size + len(self.hand))

        # Return action and action cache to game, so actions can be applied to other players.
        return self_cache, other_cache


    def buy_phase(self, table):
        pp = self.purchasing_power + self.extra_treasure
        extra = ' + extra' if self.extra_treasure else ''
        while self.num_buys:
            print('Value of treasures{}: {}, buys remaining: {}'.format(extra, pp, self.num_buys))
            print('On the table for purchase:')
            print(table)

            purchasable = table.get_purchasable_cards(pp)
            prompt_str = 'Make a purchase or ENTER to skip'
            choice = get_choice(prompt_str, choice_set=purchasable + [None])
            if choice == None:
                break

            # Buy card and update pp
            card = table.buy_idx(choice)
            print('{} bought {}\n'.format(self.name, card))
            pp -= card.cost
            self.num_buys -= 1
            self.deck.add_new(card)
        print('{} concludes buy phase\n'.format(self.name))


    def cleanup_hand(self):
        self.deck.discard(self.hand)
        self.extra_treasure = 0
        self.num_actions = 1
        self.num_buys = 1
        self.throne_room_action = None


    def draw_cards(self):
        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand = new_hand
        print('{} draws {} cards\n'.format(self.name, NUM_TO_DRAW))

        # Debug: Should always start with a full hand
        assert(len(self.hand) == NUM_TO_DRAW)


    def compute_score(self):
        """
        Using the deck's card counts, calculate the number of victory points
        the player has.
        """
        return self.deck.counts[ESTATE] * 1 \
            + self.deck.counts[DUTCHY] * 3 \
            + self.deck.counts[PROVINCE] * 6 \
            + self.deck.counts[CURSE] * -1 \
            + self.deck.counts[GARDENS] * floor(self.deck.size / 10)
