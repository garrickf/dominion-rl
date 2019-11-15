from enum import Enum
from colorama import Fore, Back, Style
from util import get_integer

"""
Presents the implementation of the card class, as well as default card instances
used in the game.
"""

# Create an enum of card types
CARD_TYPES = Enum('CARD_TYPES', 'VICTORY TREASURE ACTION CURSE')
TREASURE_TO_COLOR = {
    'Copper': Fore.RED,
    'Silver': Fore.WHITE,
    'Gold': Fore.YELLOW,
}
TYPE_TO_COLOR = {
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
            color = TREASURE_TO_COLOR[self.name]
        else: 
            color = TYPE_TO_COLOR[self.type]
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

TREASURES = [COPPER, SILVER, GOLD]

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


def card_list_to_options(cards, only_idxs=None, can_escape=False):
    s = 'Options:\n'
    for idx, card in enumerate(cards):
        if only_idxs and idx not in only_idxs: 
            continue
        s += '{}. {}\n'.format(idx, card)

    if can_escape:
        s += 'ENTER: End action\n'
    return s

"""
See below for an example generator. A generator is responsible for:
- Returning a tuple of the choices one can make, and the prompt string of what to ask
- Printing the required info for a (human) player to make the decision

An action either induces a state change on the agent passed in, or creates a multi-
step generator function that the agent is expected to call until completion. Actions
are cased on the agent type (self, other) and the phase (immediate, buy, action,
reaction) such that actions applied to other players can induce different effects 
or processes.
"""
def chapel_action(agent, agent_type, phase, table):
    def generator():
        """
        The chapel allows a player to trash up to four cards from their hand. The 
        action is structured as a sequence up to four subactions you can escape at 
        any time.
        """
        choices = [i for i in range(len(agent.hand))] + [None] # Can finish action at any time
        to_remove_idxs = []
        for i in range(4):
            
            # Prompt agent to make choice from set of discrete choices
            print(card_list_to_options(agent.hand, only_idxs=choices, can_escape=True))
            prompt_str = 'Choose a card to trash ({}/4)'.format(i+1)
            choice = (yield choices, prompt_str)

            assert(choice == None or type(choice) == int)
            if choice == None:
                break
            
            print('{} trashed {}'.format(agent.name, agent.hand[choice]))
            agent.deck.trash(agent.hand[choice])
            to_remove_idxs.append(choice)
            choices = [i for i in choices if i != choice]
        agent.hand = [card for idx, card in enumerate(agent.hand) if idx not in to_remove_idxs]
        return

    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
    else:
        return None
chapel_action.affects_others=False
CHAPEL = Card('Chapel', CARD_TYPES.ACTION, cost=2, action=chapel_action, 
              card_desc='Trash up to four cards from your hand.')


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
VILLAGE = Card('Village', CARD_TYPES.ACTION, cost=3, action=village_action,
               card_desc='+1 card. +2 actions.')


def festival_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        agent.num_actions += 2
        agent.num_buys += 1
        agent.extra_treasure += 2
festival_action.affects_others = False
FESTIVAL = Card('Festival', CARD_TYPES.ACTION, cost=5, action=festival_action, card_desc='+2 actions. +1 buy. +(2)')


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
MARKET = Card('Market', CARD_TYPES.ACTION, cost=5, action=market_action, card_desc='+1 card. +1 action. +1 buy. +(1)')


def witch_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(2)
        agent.hand += newCards
        print('You drew {}'.format(card_list_to_string(newCards)))
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        if table.get_card(CURSE):
            agent.deck.add_new(CURSE)
            print('{} gains a {}!'.format(agent.name, CURSE))
        else:
            print('{} cannot gain a {} because there are no more'.format(agent.name, CURSE))
witch_action.affects_others = True
WITCH = Card('Witch', CARD_TYPES.ACTION, cost=5, action=witch_action, card_desc='+2 cards. Each other player gains a curse.')


def filter_actions(arr, cond):
    """
    Valid actions should be labelled 0 to n, yet they may refer to indexes
    in the full list. We can unpack a zipped array and rezip to get two in-order 
    sequences of the original indices and the cards. The condition should be
    a lambda function accepting a card and an index.
    """
    zipped = [(i, v) for i, v in enumerate(arr) if cond(v, i)]
    action_to_idx, cards = zip(*zipped)
    action_set = list(range(len(cards)))

    return action_to_idx, cards, action_set


def mine_action(agent, agent_type, phase, table):
    def generator():
        all_actions = agent.hand
        cond = lambda card, i: card in TREASURES
        action_to_idx, cards, action_set = filter_actions(all_actions, cond)
        
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Trash a treasure from your hand'
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.trash(card)
        print('{} trashed {}'.format(agent.name, card)) # TODO: migrate to player
        worth = card.cost + 3

        # TODO: can purchase kind of hacky right now, since table order isn't fixed.
        action_to_idx, cards, action_set = filter_actions(TREASURES, lambda card, i: table.can_purchase(i, worth))
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Gain a treasure costing up to (3) more than what you trashed'

        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = table.buy_idx(action_to_idx[choice])
        print('{} obtained {}'.format(agent.name, card)) # TODO: migrate to player
        agent.deck.add_new(card)
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
    else:
        return None
mine_action.affects_others = False
MINE = Card('Mine', CARD_TYPES.ACTION, cost=5, action=mine_action, card_desc='You may trash a treasure from your hand. Gain a treasure to your hand costing up to (3) more than it.')


def moneylender_action(agent, agent_type, phase, table):
    def generator():
        all_actions = agent.hand
        cond = lambda card, i: card == COPPER
        action_to_idx, cards, action_set = filter_actions(all_actions, cond)
        
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Trash a Copper from your hand'
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.trash(card)
        print('{} trashed {}'.format(agent.name, card)) # TODO: migrate to player
        agent.extra_treasure += 3
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
    else:
        return None
moneylender_action.affects_others = False
MONEYLENDER = Card('Moneylender', CARD_TYPES.ACTION, cost=4, action=moneylender_action, card_desc='You may trash a Copper from your hand for +(3)')


def remodel_action(agent, agent_type, phase, table):
    def generator():
        all_actions = agent.hand
        cond = lambda card, i: True
        action_to_idx, cards, action_set = filter_actions(all_actions, cond)
        
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Trash a card from your hand'
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.trash(card)
        print('{} trashed {}'.format(agent.name, card)) # TODO: migrate to player
        
        worth = card.cost + 2
        action_to_idx, cards, action_set = filter_actions(table.cards, lambda card, i: table.can_purchase(i, worth))
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Gain a card costing up to ({} + {} = {})'.format(card.cost, 2, worth)
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = table.buy_idx(action_to_idx[choice])
        print('{} obtained {}'.format(agent.name, card)) # TODO: migrate to player
        agent.deck.add_new(card)
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
    else:
        return None
remodel_action.affects_others = False
REMODEL = Card('Remodel', CARD_TYPES.ACTION, cost=4, action=remodel_action, card_desc='Trash a card from your hand. Gain a card costing up to (2) more than it.')



