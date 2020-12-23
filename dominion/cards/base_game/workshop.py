"""Workshop: Gain a card costing up to (4).
"""
from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import card_to_str, options_to_str


def get_buy_options(table):
    value = 4
    options = {}
    for idx, card in enumerate(table):
        left = table[card]
        if card.cost <= value and left > 0:
            options[idx] = card.name
    return options


class WorkshopEvent(Event):
    def forward(self, game_ctx, player):
        options = get_buy_options(game_ctx.table)
        player.show(options_to_str(options))

        prompt_str = "Gain a card costing up to (4)"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        card = game_ctx.table.buy(c, player, free=True)
        print(f"Player acquired {card_to_str(card)}\n")


class Workshop(ActionCard):
    def __init__(self):
        super().__init__(name="Workshop", cost=3, desc="Gain a card costing up to (4).")

    def play(self, game_ctx, player):
        events = [WorkshopEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


WORKSHOP = Workshop()
