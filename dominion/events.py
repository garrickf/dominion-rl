""" Event classes TODO: docstring
"""

from abc import ABC, abstractmethod
from dominion.prettyprint import hand_to_str, table_to_str
from .common import DeckPile, CardType


""" Helper functions that specifically edit the game context
"""
def get_num_events(ctx, target):
    """ Assumes the event passed is sourced from itself
    """
    total = 1
    for event in ctx.event_queue:
        if type(event).__name__ == type(target).__name__:
            total += 1
        else:
            break
    return total

def clear_events_ahead_of_self(ctx, target):
    """ Clears all events ahead of self.
    """
    for idx, event in enumerate(ctx.event_queue):
        if type(event).__name__ != type(target).__name__:
            ctx.event_queue = ctx.event_queue[idx:]
            return

""" Helper functions for getting options
"""
def get_playable_actions_as_options(cards):
    """ Takes a list of cards and returns a dict from index to string option
    """
    options = {}
    for idx, card in enumerate(cards):
        if card.kind == CardType.ACTION:
            options[idx] = card.name
    return options


def get_purchasable_cards_as_options(table, player):
    options = {}
    for idx, card in enumerate(table):
        left = table[card]
        if card.cost <= player.treasure and left > 0:
            options[idx] = card.name
    return options

class Event:
    def __init__(self, *, target):
        self.target = target

    @abstractmethod
    def forward(self, game_ctx, player):
        """ game_ctx: Game context
        player: Player object
        """
        pass


class PlayActionEvent(Event):
    def forward(self, game_ctx, player):
        player.show(hand_to_str(player.hand))

        options = get_playable_actions_as_options(player.hand)
        if not options:
            player.show('No actions are available to be played.\n')
            clear_events_ahead_of_self(game_ctx, self)
            return

        prompt_str = 'Play an action ({} remaining)'.format(
            get_num_events(game_ctx, self))
        c = player.get_input(prompt_str, options)

        action_card = player.hand[c]
        action_card.play(game_ctx, player)
        player.deck.move([action_card],
                         from_pile=DeckPile.HAND,
                         to_pile=DeckPile.DISCARD)


class BuyEvent(Event):
    def forward(self, game_ctx, player):
        player.show(table_to_str(game_ctx.table))
        options = get_purchasable_cards_as_options(game_ctx.table, player)
        if not options:
            player.show('Cannot afford anything this turn.\n')
            clear_events_ahead_of_self(game_ctx, self)
            return

        n = get_num_events(game_ctx, self)
        prompt_str = 'Buy a card on the board ({} buy{} left)'.format(
            n, 's' if n != 1 else '')
        c = player.get_input(prompt_str, options)
        card = game_ctx.table.buy(c, player)
        # TODO: transfer to game announcement system...
        print('Player bought {}'.format(card))


class CleanupEvent(Event):
    def forward(self, game_ctx, player):
        player.reset_modifiers()  # Clear spent, any status effects
        player.deck.draw_cards(n=5, replace_hand=True)
        player.show('Drawing 5 cards and ending turn.\n')


class SetupEvent(Event):
    def forward(self, game_ctx, player):
        # TODO: print message that game begins with a certain deck of cards
        # Separate game log info with the data shown to a player...
        print('Drawing 5 cards.')
        player.deck.draw_cards(n=5, replace_hand=True)
        pass
