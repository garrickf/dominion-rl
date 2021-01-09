""" Festival: +2 actions, +1 buy, +(2)
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, PlayActionEvent, BuyEvent


class FestivalEvent(Event):
    def forward(self, game_ctx, player):
        player.set_modifier("extra_treasure", lambda v: v + 2)


class Festival(ActionCard):
    def __init__(self):
        super().__init__(name="Festival", cost=5, desc="+2 actions. +1 buy. +(2)")

    def play(self, game_ctx, player):
        events = [
            FestivalEvent(target=player.name),
            PlayActionEvent(target=player.name),
            PlayActionEvent(target=player.name),
            BuyEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


FESTIVAL = Festival()
