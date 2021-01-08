"""Workshop: Gain a card costing up to (4).
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event
from dominion.prettyprint import card_to_str, options_to_str


def get_buy_options(supply):
    value = 4
    options = {}
    for idx, card in enumerate(supply):
        left = supply[card]
        if card.cost <= value and left > 0:
            options[idx] = card.name
    return options


class WorkshopEvent(Event):
    def forward(self, game_ctx, player):
        options = get_buy_options(game_ctx.supply)
        player.show(options_to_str(options))

        prompt_str = "Gain a card costing up to (4)"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        card = game_ctx.supply.buy(c, player, free=True)
        logging.log(
            [logging.GAME, logging.OBSERVER],
            f"{player.name} acquired {card_to_str(card)}.",
        )


class Workshop(ActionCard):
    def __init__(self):
        super().__init__(name="Workshop", cost=3, desc="Gain a card costing up to (4).")

    def play(self, game_ctx, player):
        events = [WorkshopEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


WORKSHOP = Workshop()
