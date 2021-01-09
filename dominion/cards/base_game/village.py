from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, PlayActionEvent


class VillageEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)


class Village(ActionCard):
    def __init__(self):
        super().__init__(name="Village", cost=2, desc="+1 card. +2 actions.")

    def play(self, game_ctx, player):
        events = [
            VillageEvent(target=player.name),
            PlayActionEvent(target=player.name),
            PlayActionEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)  # Takes in list


VILLAGE = Village()
