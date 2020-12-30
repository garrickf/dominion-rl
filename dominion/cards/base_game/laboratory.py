""" Laboratory: +2 cards. +1 action.
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, PlayActionEvent


class LaboratoryEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=2, replace_hand=False)


class Laboratory(ActionCard):
    def __init__(self):
        super().__init__(name="Laboratory", cost=5, desc="+2 cards. +1 action.")

    def play(self, game_ctx, player):
        events = [
            LaboratoryEvent(target=player.name),
            PlayActionEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)  # Takes in list


LABORATORY = Laboratory()
