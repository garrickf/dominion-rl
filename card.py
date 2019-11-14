from enum import Enum
from colorama import Fore, Back, Style
from util import get_integer

"""
Presents the implementation of the card class, as well as default card instances
used in the game.
"""

# Create an enum of card types
CARD_TYPES = Enum('CARD_TYPES', 'VICTORY TREASURE ACTION CURSE')
treasure_to_color = {
    'Copper': Fore.RED,
    'Silver': Fore.WHITE,
    'Gold': Fore.YELLOW,
}
type_to_color = {
    CARD_TYPES.VICTORY: Fore.GREEN,
    CARD_TYPES.ACTION: Fore.CYAN,
    CARD_TYPES.CURSE: Fore.BLUE,
}


class Card:
    """
    A card critically has a name and cost.
    """
    def __init__(self, name, kind, **kwargs):
        self.name = name
        self.type = kind

        self.card_desc = None

        # Use kwargs and dict representation of object to set multiple props at once
        # For action, victory_points, treasure_value
        allowed_keys = {'action', 'victory_points', 'treasure_value', 'cost', 'card_desc'}
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
        # TODO: add description, type, flesh out how action works


    def set_victory_points(self, points):
        self.victory_points = points


    def set_treasure_value(self, value):
        self.treasure_value = value


    def __str__(self):
        """
        Prints a string represenation of the card; useful during gameplay.
        """
        color = Fore.WHITE
        if self.type == CARD_TYPES.TREASURE:
            color = treasure_to_color[self.name]
        else: 
            color = type_to_color[self.type]
        return '{}{}{}'.format(color, self.name, Style.RESET_ALL)


    @property
    def description(self):
        if self.type == CARD_TYPES.TREASURE:
            return Style.DIM + 'Treasure card worth {}.'.format(self.treasure_value) + Style.RESET_ALL
        elif self.type == CARD_TYPES.VICTORY and not self.card_desc:
            return Style.DIM + 'Victory card worth {} VP.'.format(self.victory_points) + Style.RESET_ALL
        elif self.type == CARD_TYPES.CURSE:
            return Style.DIM + '-1 VP for each curse in deck.' + Style.RESET_ALL
        else: # Action
            return Style.DIM + self.card_desc + Style.RESET_ALL

"""
Victory cards
"""

PROVINCE = Card('Province', CARD_TYPES.VICTORY, cost=8, victory_points=6)
DUTCHY = Card('Dutchy', CARD_TYPES.VICTORY, cost=5, victory_points=3)
ESTATE = Card('Estate', CARD_TYPES.VICTORY, cost=2, victory_points=1)
GARDENS = Card('Gardens', CARD_TYPES.VICTORY, cost=4, victory_points=None, card_desc='Worth 1 VP per 10 cards you have (round down).')

"""
Treasure cards
"""

GOLD = Card('Gold', CARD_TYPES.TREASURE, cost=6, treasure_value=3)
SILVER = Card('Silver', CARD_TYPES.TREASURE, cost=3, treasure_value=2)
COPPER = Card('Copper', CARD_TYPES.TREASURE, cost=0, treasure_value=1)

"""
Curse card
"""

CURSE = Card('Curse', CARD_TYPES.CURSE, cost=0, victory_points=-1)

"""
Action cards. Actions work as functions that directly prompt users and modify 
user state.
"""

# Agent: self or other, phase = action, buy, immediate
AGENT_TYPES = Enum('AGENT_TYPES', 'SELF OTHER')
PHASE_TYPES = Enum('PHASE_TYPES', 'IMMEDIATE ACTION BUY')


def card_list_to_string(cards):
    s = ''
    for card in cards:
        s += '{}, '.format(card)
    return s[:-2] # Strip remaining two characters


def chapel_action(agent, agent_type, phase, table):
    print('I am supposed to do something!!!')
CHAPEL = Card('Chapel', CARD_TYPES.ACTION, cost=2, action=chapel_action, card_desc='Trash up to four cards from your hand.')


def smithy_action(agent, agent_type, phase, table):
    """
    If the agent is self and the phase is immediate, draw three cards into hand.
    """
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(3)
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.hand += newCards
smithy_action.affects_others = False
SMITHY = Card('Smithy', CARD_TYPES.ACTION, cost=4, action=smithy_action, card_desc='+3 cards.')


def village_action(agent, agent_type, phase, table):
    """
    If the agent is self and the phase is immediate, draw one card and add 2 actions.
    """
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.hand += newCards
        agent.num_actions += 2
village_action.affects_others = False
VILLAGE = Card('Village', CARD_TYPES.ACTION, cost=3, action=village_action, card_desc='+1 card. +2 actions.')


def festival_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        agent.num_actions += 2
        agent.num_buys += 1
        agent.extra_treasure += 2
festival_action.affects_others = False
FESTIVAL = Card('Festival', CARD_TYPES.ACTION, cost=5, action=festival_action, card_desc='+2 actions. +1 buy. +2 treasure.')


def council_room_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(4)
        agent.hand += newCards
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.num_buys += 1
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        agent.hand += newCards
        print('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
council_room_action.affects_others = True # Uh oh
COUNCIL_ROOM = Card('Council Room', CARD_TYPES.ACTION, cost=5, action=council_room_action, card_desc='+4 cards. +1 buy. Each other player draws a card.')


def laboratory_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(2)
        agent.hand += newCards
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.num_actions += 1
laboratory_action.affects_others = False
LABORATORY = Card('Laboratory', CARD_TYPES.ACTION, cost=5, action=laboratory_action, card_desc='+2 cards. +1 action.')


def market_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        agent.hand += newCards
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.num_actions += 1
        agent.num_buys += 1
        agent.extra_treasure += 1
market_action.affects_others = False
MARKET = Card('Market', CARD_TYPES.ACTION, cost=5, action=market_action, card_desc='+1 card. +1 action. +1 buy. +1 treasure.')


def witch_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(2)
        agent.hand += newCards
        print('You drew {}'.format(card_list_to_string(newCards)))
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        table.get_card(CURSE)
        agent.deck.add_new(CURSE)
        print('{} gains a {}!'.format(agent.name, CURSE))
witch_action.affects_others = True
WITCH = Card('Witch', CARD_TYPES.ACTION, cost=5, action=witch_action, card_desc='+2 cards. Each other player gains a curse.')


def mine_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        # Trash a treasure from hand
        agent.display_hand()
        choice = get_integer('You can trash a treasure from your hand or ENTER to abort: ')
        if choice == None: # TODO: more rigorous error checking
            return
        card = agent.hand.pop(choice)
        agent.deck.trash(card)
        pp = card.cost + 3
        print(table)
        choice = get_integer('Pick a treasure costing up to 3 more than the card you trashed: ')
        if choice == None: # TODO: more rigorous error checking
            return
        
        while not table.can_purchase(choice, pp, card_type_only=CARD_TYPES.TREASURE):
            print('Can\'t buy that, try again!')
            choice = get_integer('Pick a treasure costing up to 3 more than the card you trashed: ')
            if choice == None:
                return

        card = table.buy_idx(choice)
        agent.deck.add_new(card)
mine_action.affects_others = False
MINE = Card('Mine', CARD_TYPES.ACTION, cost=5, action=mine_action, card_desc='You may trash a treasure from your hand. Gain a treasure to your hand costing up to 3 more than it.')
