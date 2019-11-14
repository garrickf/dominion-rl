from enum import Enum
from colorama import Fore, Back, Style

"""
Define the card class.
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
    A card critically has a name, cost, and starting pile size.
    """
    def __init__(self, name, kind, init_size, **kwargs):
        self.name = name
        self.type = kind
        self.init_size = init_size

        # Use kwargs and dict representation of object to set multiple props at once
        # For action, victory_points, treasure_value
        allowed_keys = {'action', 'victory_points', 'treasure_value', 'cost', 'action_description'}
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
        elif self.type == CARD_TYPES.VICTORY:
            return Style.DIM + 'Victory card worth {} VP.'.format(self.victory_points) + Style.RESET_ALL
        elif self.type == CARD_TYPES.CURSE:
            return Style.DIM + '-1 VP for each curse in deck.' + Style.RESET_ALL
        else: # Action
            return Style.DIM + self.action_description + Style.RESET_ALL

"""
Victory cards
"""

PROVINCE = Card('Province', CARD_TYPES.VICTORY, 12, cost=8, victory_points=6)
DUTCHY = Card('Dutchy', CARD_TYPES.VICTORY, 12, cost=5, victory_points=3)
ESTATE = Card('Estate', CARD_TYPES.VICTORY, 12, cost=2, victory_points=1)

"""
Treasure cards
"""

GOLD = Card('Gold', CARD_TYPES.TREASURE, 30, cost=6, treasure_value=3)
SILVER = Card('Silver', CARD_TYPES.TREASURE, 40, cost=3, treasure_value=2)
COPPER = Card('Copper', CARD_TYPES.TREASURE, 60, cost=0, treasure_value=1)

"""
Curse card
"""

CURSE = Card('Curse', CARD_TYPES.CURSE, 30, cost=0, victory_points=-1)

"""
Action cards
"""

# Agent: self or other, phase = action, buy, immediate
AGENT_TYPES = Enum('AGENT_TYPES', 'SELF OTHER')
PHASE_TYPES = Enum('PHASE_TYPES', 'IMMEDIATE ACTION BUY')


def card_list_to_string(cards):
    s = ''
    for card in cards:
        s += '{}, '.format(card)
    return s[:-2] # Strip remaining two characters


def chapel_action(agent, phase):
    print('I am supposed to do something!!!')
CHAPEL = Card('Chapel', CARD_TYPES.ACTION, 10, cost=2, action=chapel_action, action_description='Trash up to four cards from your hand.')


def smithy_action(agent, agent_type, phase):
    """
    If the agent is self and the phase is immediate, draw three cards into hand.
    """
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(3)
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.hand += newCards
smithy_action.affects_others = False
SMITHY = Card('Smithy', CARD_TYPES.ACTION, 10, cost=4, action=smithy_action, action_description='+3 cards.')


def village_action(agent, agent_type, phase):
    """
    If the agent is self and the phase is immediate, draw one card and add 2 actions.
    """
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        print('You drew {}'.format(card_list_to_string(newCards)))
        agent.hand += newCards
        agent.num_actions += 2
village_action.affects_others = False
VILLAGE = Card('Village', CARD_TYPES.ACTION, 10, cost=3, action=village_action, action_description='+1 card. +2 actions.')


def festival_action(agent, agent_type, phase):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        agent.num_actions += 2
        agent.num_buys += 1
        agent.extra_treasure += 2
festival_action.affects_others = False
FESTIVAL = Card('Festival', CARD_TYPES.ACTION, 10, cost=5, action=festival_action, action_description='+2 actions. +1 buy. +2 treasure.')


def council_room_action(agent, agent_type, phase):
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
COUNCIL_ROOM = Card('Council Room', CARD_TYPES.ACTION, 10, cost=5, action=council_room_action, action_description='+4 cards. +1 buy. Each other player draws a card.')

