""" Council Room: +4 cards, +1 buy, each other player draws a card
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event, BuyEvent


class CouncilRoomEventSelf(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=4, replace_hand=False)


class CouncilRoomEventOther(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)


class CouncilRoom(ActionCard):
    def __init__(self):
        super().__init__(
            name="Council Room",
            cost=5,
            desc="+4 cards. +1 buy. Each other player draws a card.",
        )

    def play(self, game_ctx, player):
        events = [CouncilRoomEventSelf(target=player.name)]

        for other_player_name in game_ctx.get_other_players(player.name):
            events.append(CouncilRoomEventOther(target=other_player_name))

        events.append(BuyEvent(target=player.name))
        game_ctx.add_events(events, where=QueuePosition.FRONT)


COUNCIL_ROOM = CouncilRoom()
