"""Market: +1 card. +1 action. +1 buy. +(1)
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, PlayActionEvent, BuyEvent


class MarketEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)
        player.set_modifier("extra_treasure", lambda v: v + 1)


class Market(ActionCard):
    def __init__(self):
        super().__init__(name="Market", cost=5, desc="+1 card. +1 action. +1 buy. +(1)")

    def play(self, game_ctx, player):
        events = [
            MarketEvent(target=player.name),
            PlayActionEvent(target=player.name),
            BuyEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


MARKET = Market()
