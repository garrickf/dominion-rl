"""Smithy: +3 cards.
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event


class SmithyEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=3, replace_hand=False)


class Smithy(ActionCard):
    def __init__(self):
        super().__init__(name="Smithy", cost=4, desc="+3 cards.")

    def play(self, game_ctx, player):
        events = [
            SmithyEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


SMITHY = Smithy()
