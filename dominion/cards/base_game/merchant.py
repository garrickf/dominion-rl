""" Merchant: +1 Card. +1 Action. The first time you play a Silver this turn, 
+(1).
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, PlayActionEvent

from .silver import SILVER


class MerchantEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)

        if SILVER in player.hand:
            player.set_modifier("extra_treasure", lambda v: v + 1)


class Merchant(ActionCard):
    def __init__(self):
        super().__init__(
            name="Merchant",
            cost=3,
            desc="+1 Card. +1 Action. The first time you play a Silver this turn, +(1).",
        )

    def play(self, game_ctx, player):
        events = [
            MerchantEvent(target=player.name),
            PlayActionEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


MERCHANT = Merchant()
