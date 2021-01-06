""" Mine TODO: docstring
"""

from dominion.cards import ActionCard
from dominion.common import CardType, DeckPile, QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import card_to_str, hand_to_str, options_to_str


def get_treasures_as_options(cards):
    """Takes a list of cards and returns a dict from index to string option"""
    options = {}
    for idx, card in enumerate(cards):
        if card.kind == CardType.TREASURE:
            options[idx] = card.name
    return options


def get_eligible_treasures_as_options(supply, value):
    """Takes a list of cards and returns a dict from index to string option"""
    options = {}
    for idx, card in enumerate(supply):
        left = supply[card]
        if card.kind == CardType.TREASURE and card.cost <= value and left > 0:
            options[idx] = card.name
    return options


class MineEvent(Event):
    def forward(self, game_ctx, player):
        """The Mine card allows a player to trash any treasure from their hand
        and gain a treasure costing up to (3) more than it.
        """

        player.show(hand_to_str(player.hand))

        options = get_treasures_as_options(player.hand)
        if not options:
            player.show("No treasures are available to trash.\n")
            # If there are any other Events like this one, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        prompt_str = "Choose a treasure to trash from your hand"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        to_trash = player.hand[c]
        new_value = to_trash.cost + 3
        # TODO: test
        player.deck.trash([to_trash])
        options = get_eligible_treasures_as_options(game_ctx.supply, new_value)

        player.show(options_to_str(options))
        prompt_str = f"Gain a treasure to costing up to ({new_value})"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        card = game_ctx.supply.buy(c, player, free=True)
        print("Player acquired {}\n".format(card_to_str(card)))


class Mine(ActionCard):
    def __init__(self):
        super().__init__(
            name="Mine",
            cost=5,
            desc="You may trash a treasure from your hand. Gain a treasure to your hand costing up to (3) more than it.",
        )

    def play(self, game_ctx, player):
        events = [MineEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


MINE = Mine()
