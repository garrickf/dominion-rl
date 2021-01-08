""" Moneylender: You may trash a Copper from your hand for (+3).
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import hand_to_str


def get_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card.name == "Copper":
            options[idx] = card.name
    return options


class MoneylenderEvent(Event):
    def forward(self, game_ctx, player):
        player.show(hand_to_str(player.hand))

        options = get_options(player.hand)
        if not options:
            player.show("No Coppers are available to trash.\n")
            # If there are any other Events like this one, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        prompt_str = "Choose a Copper to trash from your hand"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        to_trash = player.hand[c]
        player.deck.trash([to_trash])
        player.set_modifier("extra_treasure", lambda v: v + 3)

        logging.log(
            [logging.GAME, logging.OBSERVER],
            f"{player.name} trashed a Copper to get (+3)",
        )


class Moneylender(ActionCard):
    def __init__(self):
        super().__init__(
            name="Moneylender",
            cost=4,
            desc="You may trash a Copper from your hand for +(3)",
        )

    def play(self, game_ctx, player):
        events = [MoneylenderEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


MONEYLENDER = Moneylender()
