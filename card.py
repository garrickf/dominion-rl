from enum import Enum
from colorama import Fore, Back, Style
from util import get_integer
from utilities.log import Log

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
game_log = Log()


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
        return '{}{}{}'.format(color, self.name, Fore.WHITE)


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

VICTORY_CARDS = [PROVINCE, DUTCHY, ESTATE, GARDENS]

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


def card_list_to_options(cards, only_idxs=None, can_escape=False, verbose=False):
    if not verbose:
        s = 'Options:\n'
        for idx, card in enumerate(cards):
            if only_idxs and idx not in only_idxs: 
                continue
            s += '{}. {}\n'.format(idx, card)

        if can_escape:
            s += 'ENTER: End action\n'
        return s
    else:
        s = 'Options:\n'
        s += '{:<4}{:<14}{:<7}{:<}\n'.format('', 'Name', 'Cost', 'Description')
        for i, card in enumerate(cards):
            s += '{:>2}. {!s:<23} ({:>2}) | {}\n'.format(i, card, card.cost, card.description)
        
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
            
            game_log.add_message('{} trashed {}'.format(agent.name, agent.hand[choice]))
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
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.hand += newCards
smithy_action.affects_others = False
SMITHY = Card('Smithy', CARD_TYPES.ACTION, cost=4, action=smithy_action, card_desc='+3 cards.')


def village_action(agent, agent_type, phase, table):
    """
    If the agent is self and the phase is immediate, draw one card and add 2 actions.
    """
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
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
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.num_buys += 1
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        agent.hand += newCards
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
council_room_action.affects_others = True # Uh oh
COUNCIL_ROOM = Card('Council Room', CARD_TYPES.ACTION, cost=5, action=council_room_action, card_desc='+4 cards. +1 buy. Each other player draws a card.')


def laboratory_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(2)
        agent.hand += newCards
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.num_actions += 1
laboratory_action.affects_others = False
LABORATORY = Card('Laboratory', CARD_TYPES.ACTION, cost=5, action=laboratory_action, card_desc='+2 cards. +1 action.')


def market_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        agent.hand += newCards
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.num_actions += 1
        agent.num_buys += 1
        agent.extra_treasure += 1
market_action.affects_others = False
MARKET = Card('Market', CARD_TYPES.ACTION, cost=5, action=market_action, card_desc='+1 card. +1 action. +1 buy. +(1)')


def witch_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(2)
        agent.hand += newCards
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        if table.get_card(CURSE):
            agent.deck.add_new(CURSE)
            game_log.add_message('{} gains a {}!'.format(agent.name, CURSE))
        else:
            game_log.add_message('{} cannot gain a {} because there are no more'.format(agent.name, CURSE))
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
    if not zipped: # Empty, no possible actions
        return [], [], []
    action_to_idx, cards = zip(*zipped)
    action_set = list(range(len(cards)))

    return action_to_idx, cards, action_set


def mine_action(agent, agent_type, phase, table):
    def generator():
        all_actions = agent.hand
        cond = lambda card, i: card in TREASURES
        action_to_idx, cards, action_set = filter_actions(all_actions, cond)
        
        action_set += [None]
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Trash a treasure from your hand'
        choice = (yield action_set, prompt_str)
        assert(choice != None)

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.trash(card)
        game_log.add_message('{} trashed {}'.format(agent.name, card)) # TODO: migrate to player
        worth = card.cost + 3

        action_to_idx, cards, action_set = filter_actions(TREASURES, lambda card, i: table.can_purchase_card(card, worth))
        action_set += [None]
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Gain a treasure costing up to (3) more than what you trashed'

        choice = (yield action_set, prompt_str)
        assert(choice != None)

        card = table.buy_idx(action_to_idx[choice])
        game_log.add_message('{} obtained {}'.format(agent.name, card)) # TODO: migrate to player
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
        
        action_set += [None]
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'Trash a Copper from your hand'
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.trash(card)
        game_log.add_message('{} trashed {}'.format(agent.name, card)) # TODO: migrate to player
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
        
        action_set += [None] # Optional
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'You may trash a card from your hand'
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.trash(card)
        game_log.add_message('{} trashed {}'.format(agent.name, card)) # TODO: migrate to player
        
        worth = card.cost + 2
        action_to_idx, cards, action_set = filter_actions(table.cards, lambda card, i: table.can_purchase(i, worth))
        action_set += [None]
        print(card_list_to_options(cards, can_escape=True, verbose=True))
        prompt_str = 'Gain a card costing up to ({} + {} = {})'.format(card.cost, 2, worth)
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = table.buy_idx(action_to_idx[choice])
        game_log.add_message('{} obtained {}'.format(agent.name, card)) # TODO: migrate to player
        agent.deck.add_new(card)
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
    else:
        return None
remodel_action.affects_others = False
REMODEL = Card('Remodel', CARD_TYPES.ACTION, cost=4, action=remodel_action, card_desc='Trash a card from your hand. Gain a card costing up to (2) more than it.')


def artisan_action(agent, agent_type, phase, table):
    def generator():
        worth = 5
        action_to_idx, cards, action_set = filter_actions(table.cards, lambda card, i: table.can_purchase(i, worth))
        print(card_list_to_options(cards, can_escape=True, verbose=True))
        action_set += [None]
        prompt_str = 'Gain a card to your hand costing up to (5)'
        choice = (yield action_set, prompt_str)

        if choice == None:
            return

        card = table.buy_idx(action_to_idx[choice])
        game_log.add_message('{} added {} to hand'.format(agent.name, card)) # TODO: migrate to player
        agent.hand.append(card)
        agent.deck.count(card)

        all_actions = agent.hand
        cond = lambda card, i: True
        action_to_idx, cards, action_set = filter_actions(all_actions, cond)
        
        print(card_list_to_options(cards, can_escape=False, verbose=True))
        prompt_str = 'Put a card from your hand onto your deck'
        choice = (yield action_set, prompt_str)

        assert(choice != None)

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.push(card)
        game_log.add_message('{} put {} on top of their deck'.format(agent.name, card)) # TODO: migrate to player
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
    else:
        return None
artisan_action.affects_others = False
ARTISAN = Card('Artisan', CARD_TYPES.ACTION, cost=6, action=artisan_action, card_desc='Gain a card to your hand costing up to (5). Put a card from your hand onto your deck.')


def merchant_action(agent, agent_type, phase, table):
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        newCards = agent.deck.draw(1)
        agent.hand += newCards
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.num_actions += 1
    elif agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.BUY:
        if SILVER in agent.hand:
            # Silvers would be autoplayed
            agent.extra_treasure += 1
merchant_action.affects_others = False
MERCHANT = Card('Merchant', CARD_TYPES.ACTION, cost=3, action=merchant_action, card_desc='+1 Card. +1 Action. The first time you play a Silver this turn, +(1).')


def bureaucrat_action(agent, agent_type, phase, table):
    def generator():
        """
        Other players must reveal a victory card and put it on top of their deck.
        """
        agent.display_hand()
        cond = lambda card, i: card in VICTORY_CARDS
        action_to_idx, cards, action_set = filter_actions(agent.hand, cond)
        
        if not cards:
            game_log.add_message('{} reveals their hand: {}'.format(agent.name, card_list_to_string(agent.hand)))
            return

        print(card_list_to_options(cards, can_escape=False))
        prompt_str = 'Reveal a victory card and put it onto your deck'
        choice = (yield action_set, prompt_str)
        
        assert(choice != None)

        card = agent.hand.pop(action_to_idx[choice])
        game_log.add_message('{} reveals {} and puts in onto their deck'.format(agent.name, card))
        agent.deck.push(card)
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        if table.get_card(SILVER):
            agent.deck.add_new(SILVER)
            game_log.add_message('{} gains a {}!'.format(agent.name, SILVER))
        else:
            game_log.add_message('{} cannot gain a {} because there are no more'.format(agent.name, SILVER))
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
bureaucrat_action.affects_others = True
BUREAUCRAT = Card('Bureaucrat', CARD_TYPES.ACTION, cost=4, action=bureaucrat_action, card_desc='Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it onto their deck (or reveals a hand with no Victory cards).')


def militia_action(agent, agent_type, phase, table):
    def generator():
        """
        Other players must discard down to three cards.
        """
        agent.display_hand()
        cond = lambda card, i: True
        action_to_idx, cards, action_set = filter_actions(agent.hand, cond)
        
        to_remove_idxs = []
        while len(agent.hand) - len(to_remove_idxs) > 3:
            print(card_list_to_options(agent.hand, only_idxs=action_set, can_escape=False))
            prompt_str = 'Choose a card to discard'
            choice = (yield action_set, prompt_str)

            assert(choice != None)
            
            game_log.add_message('{} discarded {}'.format(agent.name, agent.hand[choice]))
            agent.deck.trash(agent.hand[choice])
            to_remove_idxs.append(choice)
            action_set = [i for i in action_set if i != choice]
        
        agent.hand = [card for idx, card in enumerate(agent.hand) if idx not in to_remove_idxs]
        return
    
    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        agent.extra_treasure += 2
    elif agent_type == AGENT_TYPES.OTHER and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
militia_action.affects_others = True
MILITIA = Card('Militia', CARD_TYPES.ACTION, cost=4, action=militia_action, card_desc='+(2). Each other player discards down to three cards in hand.')


def workshop_action(agent, agent_type, phase, table):
    def generator():
        """
        Gain a card costing up to 4
        """
        cond = lambda card, i: table.can_purchase_card(card, 4)

        action_to_idx, cards, action_set = filter_actions(table.cards, cond)
        action_set += [None] # Optional
        print(card_list_to_options(cards, can_escape=True, verbose=True))
        prompt_str = 'Gain a card costing up to (4).'

        choice = (yield action_set, prompt_str)
        
        if choice == None:
            return

        card = table.buy_idx(action_to_idx[choice])
        game_log.add_message('{} obtained {}'.format(agent.name, card)) # TODO: migrate to player
        agent.deck.add_new(card)
        return

    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
workshop_action.affects_others = False
WORKSHOP = Card('Workshop', CARD_TYPES.ACTION, cost=3, action=workshop_action, card_desc='Gain a card costing up to (4).')


def throne_room_action(agent, agent_type, phase, table):
    def generator():
        """
        Pick an action card and execute it twice
        """
        cond = lambda card, i: card.type == CARD_TYPES.ACTION

        action_to_idx, cards, action_set = filter_actions(agent.hand, cond)
        action_set += [None] # Optional
        print(card_list_to_options(cards, can_escape=True))
        prompt_str = 'You may play an action card from your hand twice.'

        choice = (yield action_set, prompt_str)
        
        if(choice == None):
            return

        card = agent.hand.pop(action_to_idx[choice])
        agent.deck.discard([card])

        game_log.add_message('{} played {}'.format(agent.name, card)) # TODO: migrate to player
        agent.spare_action = card.action
        agent.spare_action_plays = 2
        return

    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
throne_room_action.affects_others = False
THRONE_ROOM = Card('Throne Room', CARD_TYPES.ACTION, cost=4, action=throne_room_action, card_desc='You may play an action card from your hand twice.')


def vassal_action(agent, agent_type, phase, table):
    def generator():
        """
        +2. Discard the top card of the deck. If it's an action, you may play it.
        """
        agent.extra_treasure += 2

        card = agent.deck.draw(1)[0]
        agent.deck.discard([card])

        game_log.add_message('{} discarded {} from the top of their deck'.format(agent.name, card))
        if card.type != CARD_TYPES.ACTION: 
            return

        action_set = [0, None]
        print(card_list_to_options([card], can_escape=True))
        prompt_str = 'You may play this action card.'

        choice = (yield action_set, prompt_str)
        
        if(choice == None):
            return

        game_log.add_message('{} also played that {}'.format(agent.name, card))
        agent.spare_action = card.action
        return

    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
vassal_action.affects_others = False
VASSAL = Card('Vassal', CARD_TYPES.ACTION, cost=3, action=vassal_action, card_desc='+(2). Discard the top card of your deck. If it\'s an action, you may play it.')


def sentry_action(agent, agent_type, phase, table):
    def generator():
        """
        +1 card, +1 action. Look at top 2 cards of deck, trash and/or discard any number of them.
        Put the rest back on top in any order.
        """

        agent.num_actions += 1

        newCards = agent.deck.draw(1)
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.hand += newCards

        watch = agent.deck.draw(2)
        action_to_idx, cards, action_set = filter_actions(watch, lambda card, i: True)

        to_trash = []
        while len(action_set) > 0:
            print(card_list_to_options(cards, only_idxs=action_set, can_escape=True))
            prompt_str = 'Choose a card to trash, ENTER to discard instead.'

            all_actions = action_set + [None]
            choice = (yield all_actions, prompt_str)

            if choice == None:
                break

            to_trash.append(choice)
            action_set = [a for a in action_set if a != choice]

        trashed_cards = [watch[action_to_idx[i]] for i in to_trash]
        for card in trashed_cards:
            agent.deck.trash(card)
        watch = [card for i, card in enumerate(watch) if i not in to_trash]
        if trashed_cards:
            game_log.add_message('{} trashed {}'.format(agent.name, card_list_to_string(trashed_cards)))
        
        if not watch:
            return

        action_to_idx, cards, action_set = filter_actions(watch, lambda card, i: True)
        to_discard = []
        while len(action_set) > 0:
            print(card_list_to_options(cards, only_idxs=action_set, can_escape=True))
            prompt_str = 'Choose a card to discard, ENTER to place back instead.'

            all_actions = action_set + [None]
            choice = (yield all_actions, prompt_str)

            if choice == None:
                break

            to_discard.append(choice)
            action_set = [a for a in action_set if a != choice]

        discarded_cards = [watch[action_to_idx[i]] for i in to_discard]
        agent.deck.discard(discarded_cards)
        watch = [card for i, card in enumerate(watch) if i not in to_discard]
        if discarded_cards:
            game_log.add_message('{} discarded {}'.format(agent.name, card_list_to_string(discarded_cards)))

        if not watch:
            return

        action_to_idx, cards, action_set = filter_actions(watch, lambda card, i: True)
        order = []
        while len(action_set) > 0:
            print(card_list_to_options(cards, only_idxs=action_set, can_escape=False))
            prompt_str = 'Pick card to put back on deck.'

            choice = (yield action_set, prompt_str)
            assert(choice != None)

            order.append(choice)
            action_set = [a for a in action_set if a != choice]

        for i in order:
            agent.deck.push(watch[action_to_idx[i]])

        game_log.add_message('{} placed {} card(s) on top of their deck'.format(agent.name, len(order)))
        return

    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
sentry_action.affects_others = False
SENTRY = Card('Sentry',  CARD_TYPES.ACTION, cost=5, action=sentry_action, card_desc='+1 card. +1 action. Look at the top 2 cards of your deck. Trash and/or discard any number of them. Put the rest back on top in any order.')


def poacher_action(agent, agent_type, phase, table):
    def generator():
        """
        1 card, action, treasure. Discard a card per empty supply pile
        """
        agent.extra_treasure += 1
        agent.num_actions += 1
        
        newCards = agent.deck.draw(1)
        game_log.add_message('{} drew {}'.format(agent.name, card_list_to_string(newCards)))
        agent.hand += newCards

        num_empty_piles = table.num_empty_piles
        if num_empty_piles == 0:
            return

        action_to_idx, cards, action_set = filter_actions(agent.hand, lambda card, i: True)
        to_discard = []
        for i in range(num_empty_piles):
            print(card_list_to_options(cards, only_idxs=action_set, can_escape=False))
            prompt_str = 'Choose a card to discard.'

            choice = (yield action_set, prompt_str)
            assert(choice != None)

            to_discard.append(choice)
            action_set = [a for a in action_set if a != choice]

        discarded_cards = [agent.hand[action_to_idx[i]] for i in to_discard]
        agent.deck.discard(discarded_cards)
        agent.hand = [card for i, card in enumerate(agent.hand) if i not in to_discard]
        if discarded_cards:
            game_log.add_message('{} discarded {}'.format(agent.name, card_list_to_string(discarded_cards)))
        return

    if agent_type == AGENT_TYPES.SELF and phase == PHASE_TYPES.IMMEDIATE:
        return generator()
poacher_action.affects_others = False
POACHER = Card('Poacher', CARD_TYPES.ACTION, cost=4, action=poacher_action, card_desc='+1 card. +1 action. +(1). Discard a card per empty supply pile.')


KINGDOM_CARDS = [
    CHAPEL, 
    SMITHY, 
    VILLAGE, 
    FESTIVAL, 
    COUNCIL_ROOM, 
    MARKET, 
    LABORATORY, 
    WITCH, 
    GARDENS, 
    MINE, 
    MONEYLENDER, 
    REMODEL, 
    ARTISAN, 
    MERCHANT, 
    BUREAUCRAT, 
    MILITIA, 
    WORKSHOP,
    THRONE_ROOM,
    VASSAL,
    SENTRY,
    POACHER,
]