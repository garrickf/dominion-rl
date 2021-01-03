""" The Event class and its subclasses dictate the flow of the game. They are
invoked by a running Game instance and entrusted with the necessary player and game
context information to handle anything from prompting players, to managing card
purchases off the table, and more.
"""

from abc import ABC, abstractmethod

from dominion.prettyprint import (
    card_to_str,
    filter_treasures_as_str,
    hand_to_str,
    table_to_str,
)

from .common import CardType, DeckPile

""" Helper functions that edit the game context
"""


def get_num_events(ctx, target):
    """Assumes the event passed is sourced from itself"""
    total = 1
    for event in ctx.event_queue:
        if type(event).__name__ == type(target).__name__:
            total += 1
        else:
            break
    return total


def clear_events_ahead_of_self(ctx, target):
    """Clears all events ahead of self."""
    for idx, event in enumerate(ctx.event_queue):
        if type(event).__name__ != type(target).__name__:
            ctx.event_queue = ctx.event_queue[idx:]
            return


""" Helper functions for getting options
"""


def get_playable_actions_as_options(cards):
    """Takes a list of cards and returns a dict from index to string option"""
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


# TODO: for chapel, decompose
def get_all_as_options(cards):
    options = {}
    for idx, card in enumerate(cards):
        options[idx] = card.name
    return options


class Event(ABC):
    def __init__(self, target):
        """ TODO: docstring

        Args:
            target (str): The string name of the player the event acts on. TODO: allow/
                change to Player object
        """
        self.target = target

    @abstractmethod
    def forward(self, game_ctx, player):
        """All Events have a forward method which scripts what happens to the game
        and players when the event occurs.

        Args:
            game_ctx (dominion.game.GameContext): The context for the current
                game.
            player (dominion.players.Player): The player of the event
        Returns:
            None
        Raises:
            TypeError: If forward is not implemented, Python will complain.
        """
        pass

    # Allow instances to be called like functions
    def __call__(self, game_ctx, player):
        self.forward(game_ctx, player)


class PlayActionEvent(Event):
    def forward(self, game_ctx, player):
        """The first thing a player can do on their turn is play any action cards
        in their hand.

        Args:
            game_ctx (dominion.game.GameContext): The context for the current
                game.
            player (dominion.players.Player): The player of the event
        Returns:
            None
        """
        player.show(hand_to_str(player.hand))

        options = get_playable_actions_as_options(player.hand)
        if not options:
            player.show("No actions are available to be played.\n")
            # If there are any other PlayActionEvents, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        prompt_str = "Play an action ({} remaining)".format(
            get_num_events(game_ctx, self)
        )
        c = player.get_input(prompt_str, options, allow_skip=True)

        if c == "Skip":
            return

        action_card = player.hand[c]
        action_card.play(game_ctx, player)
        player.deck.move(
            [action_card], from_pile=DeckPile.HAND, to_pile=DeckPile.PLAYED
        )

        # TODO: Transfer to logging
        print("Player played {}\n".format(card_to_str(action_card)))


def get_treasures_msg(player):
    s = filter_treasures_as_str(player.hand)
    if "extra_treasure" in player.modifiers:
        s += " (+{} bonus)".format(player.modifiers["extra_treasure"])

    treasure = player.treasure
    s += " -> You have {}".format(treasure)
    s += " treasure{} to spend\n".format("s" if treasure != 1 else "")
    return s


class BuyEvent(Event):
    def forward(self, game_ctx, player):
        """The buy stage happens after a player has played any action cards.

        Args:
            game_ctx (dominion.game.GameContext): The context for the current
                game.
            player (dominion.players.Player): The player of the event
        Returns:
            None
        """
        player.show(get_treasures_msg(player))

        player.show(table_to_str(game_ctx.table))
        options = get_purchasable_cards_as_options(game_ctx.table, player)
        if not options:
            player.show("Cannot afford anything this turn.\n")
            # If there are any other BuyEvents, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        n = get_num_events(game_ctx, self)
        prompt_str = "Buy a card on the table ({} buy{} left)".format(
            n, "s" if n != 1 else ""
        )
        c = player.get_input(prompt_str, options, allow_skip=True)

        if c == "Skip":
            return

        card = game_ctx.table.buy(c, player)
        print("Player bought {}\n".format(card_to_str(card)))


# TODO: add played cards back to discard pile
class CleanupEvent(Event):
    def forward(self, game_ctx, player):
        """The CleanupEvent happens at the end of a player's turn. They lose any
        status effects that may have been applied during their turn, and they
        end by drawing five cards.

        Args:
            game_ctx (dominion.game.GameContext): The context for the current
                game.
            player (dominion.players.Player): The player of the event
        Returns:
            None
        """
        player.cleanup()  # Clear spent, any status effects
        player.deck.draw_cards(n=5, replace_hand=True)
        player.show("Drawing 5 cards and ending turn.\n")


class SetupEvent(Event):
    def forward(self, game_ctx, player):
        """The SetupEvent occurs at the start of a new game, where each player
        draws five cards.

        Args:
            game_ctx (dominion.game.GameContext): The context for the current
                game.
            player (dominion.players.Player): The player of the event
        Returns:
            None
        """
        # TODO: Separate game log info with data shown to player. Log accordingly.
        print("Drawing 5 cards.")
        player.deck.draw_cards(n=5, replace_hand=True)
        pass
