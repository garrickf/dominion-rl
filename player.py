from math import floor
from deck import Deck
from card import CARD_TYPES, AGENT_TYPES, PHASE_TYPES, ESTATE, DUTCHY, PROVINCE, CURSE, GARDENS
from util import get_integer, get_choice, colorize
from utilities.log import Log
from colorama import Style
from utilities.console import Console

# Set to 7 to debug more easily
NUM_TO_DRAW = 5
game_log = Log()

class Player:
    def __init__(self, i, game_info={}):
        """
        Every player has an active Hand and a Deck, divided between a draw pile
        and a discard pile.
        """
        self.player_number = i
        self.type = 'Human'
        self.hand = []
        self.deck = Deck()

        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand = new_hand

        self.num_actions = 1
        self.num_buys = 1
        self.extra_treasure = 0
        self.spare_action = None
        self.spare_action_plays = 1

        self.game = game_info


    @property
    def game_info(self):
        return self.game


    @game_info.setter
    def game_info(self, game_info):
        self.game = game_info


    def display_hand(self):
        s = 'Current hand:\n'
        for idx, card in enumerate(self.hand):
            s += '{}. {}\n'.format(idx, card)
        Console.log(s)


    def display_state(self):
        Console.log('{}Game Log\n{}{}\n> Playing!\n'.format(Style.DIM, game_log.recent, Style.RESET_ALL))
        Console.log(self.deck)


    @property
    def can_play_action(self):
        for card in self.hand:
            if card.type == CARD_TYPES.ACTION:
                return True
        return False


    @property
    def name(self):
        return colorize('Player {} ({})'.format(self.player_number, self.type), idx=self.player_number)
        

    @property
    def raw_name(self): 
        return 'Player {} ({})'.format(self.player_number, self.type)


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
        Returns a list of valid actions. Playing no action is always valid, though frowned
        upon.
        """
        return [idx for idx, card in enumerate(self.hand) if card.type == CARD_TYPES.ACTION] + [None]

    def choose(self, choice_set, prompt=""):
        return get_choice(prompt, choice_set=choice_set)

    def reflect(self):
        pass # This is a stub used by the ComputerPlayer to reflect on its experiences

    def execute_action(self, action, phase, self_initiated=False):
        """
        Given some action and table, run the action to completion. Some actions 
        only induce effects on the Player object; others prompt the player to do
        something in other to complete the action.
        """
        table = self.game.table

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
                    choice = self.choose(choices, prompt=prompt_str)
                    choices, prompt_str = g.send(choice)
            except:
                pass


    def action_phase(self):
        """
        During the action phase, a player can play any action card from their
        hand.
        """
        table = self.game.table
        self.display_hand()

        # Cache actions to be applied to other players and self
        other_cache = []
        self_cache = []
        while self.num_actions:
            if not self.can_play_action:
                Console.log('No actions to play.\n')
                break

            Console.log('{} action(s) left.'.format(self.num_actions))
            prompt_str = 'Play an action (0-{}) or ENTER to skip'.format(len(self.hand)-1)
            action_idx = self.choose(self.valid_actions, prompt=prompt_str)
            if action_idx == None:
                break

            card = self.hand.pop(action_idx)
            game_log.add_message('{} played {}'.format(self.name, card))
            self.deck.discard([card]) # Place into discard

            # Execute the action
            action = card.action
            self.execute_action(action, PHASE_TYPES.IMMEDIATE, self_initiated=True)
            
            if action.affects_others:
                other_cache.append(action)
            self_cache.append(action)

            # e.g. throne room and vassal can set a spare action
            while self.spare_action:
                plays = self.spare_action_plays
                spare_action = self.spare_action

                # Reset, in case another action sets it back!
                self.spare_action_plays = 1
                self.spare_action = None
                for i in range(plays):
                    self.execute_action(spare_action, PHASE_TYPES.IMMEDIATE, self_initiated=True)
                    if spare_action.affects_others:
                        other_cache.append(spare_action)
                    self_cache.append(spare_action)

            self.num_actions -= 1
            self.display_hand()
        # Console.log('{} concludes action phase\n'.format(self.name))

        # Debug: Cards should not disappear without our consent
        assert(self.deck.size == self.deck.draw_pile_size + self.deck.discard_pile_size + len(self.hand))

        # Return action and action cache to game, so actions can be applied to other players.
        return self_cache, other_cache


    def buy_phase(self):
        table = self.game.table
        pp = self.purchasing_power + self.extra_treasure
        extra = ' + extra' if self.extra_treasure else ''
        while self.num_buys:
            Console.log('Value of treasures{}: {}, buys remaining: {}'.format(extra, pp, self.num_buys))
            Console.log('On the table for purchase:')
            Console.log(table)

            purchasable = table.get_purchasable_cards(pp)
            prompt_str = 'Make a purchase or ENTER to skip'
            choice_set = purchasable if pp >= 3 else [None]
            choice = self.choose(choice_set, prompt=prompt_str)
            if choice == None:
                break

            # Buy card and update pp
            card = table.buy_idx(choice)
            game_log.add_message('{} bought {}'.format(self.name, card))
            pp -= card.cost
            self.num_buys -= 1
            self.deck.add_new(card)
        # Console.log('{} concludes buy phase\n'.format(self.name))


    def cleanup_hand(self):
        self.deck.discard(self.hand)
        self.extra_treasure = 0
        self.num_actions = 1
        self.num_buys = 1
        self.throne_room_action = None


    def draw_cards(self):
        new_hand = self.deck.draw(NUM_TO_DRAW)
        self.hand = new_hand
        game_log.add_message('{} ends turn, draws {} cards'.format(self.name, len(self.hand)))

        # Debug: Should always start with a full hand; or doesn't have enough cards
        # for a full hand
        assert(len(self.hand) == NUM_TO_DRAW or self.deck.size < NUM_TO_DRAW)


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
