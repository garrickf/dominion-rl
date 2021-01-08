""" Remodel: Trash a card from your hand. Gain a card costing up to (2) more 
than it.
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import card_to_str, hand_to_str, options_to_str


def get_trash_options(hand):
    # Any card can be trashed
    return {idx: card.name for idx, card in enumerate(hand)}


def get_buy_options(supply, value):
    options = {}
    for idx, card in enumerate(supply):
        left = supply[card]
        if card.cost <= value and left > 0:
            options[idx] = card.name
    return options


class RemodelEvent(Event):
    def forward(self, game_ctx, player):
        player.show(hand_to_str(player.hand))

        options = get_trash_options(player.hand)
        if not options:
            player.show("No cards are available to trash.\n")
            # If there are any other Events like this one, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        prompt_str = "Choose a card to trash from your hand"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        to_trash = player.hand[c]
        new_value = to_trash.cost + 2

        player.deck.trash([to_trash])
        options = get_buy_options(game_ctx.supply, new_value)

        player.show(options_to_str(options))
        prompt_str = f"Gain a card costing up to ({new_value})"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        card = game_ctx.supply.buy(c, player, free=True)
        logging.log(
            [logging.GAME, logging.OBSERVER],
            f"{player.name} trashed {card_to_str(to_trash)} and acquired {card_to_str(card)}.",
        )


class Remodel(ActionCard):
    def __init__(self):
        super().__init__(
            name="Remodel",
            cost=4,
            desc="Trash a card from your hand. Gain a card costing up to (2) more than it.",
        )

    def play(self, game_ctx, player):
        events = [RemodelEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


REMODEL = Remodel()
