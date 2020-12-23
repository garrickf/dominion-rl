""" Moat: +2 cards. When another player plays an Attack card, you may first 
reveal this from your hand, to be unaffected by it.

# TODO: create an action - reaction type card
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event
from dominion.prettyprint import hand_to_str


class MoatEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=2, replace_hand=False)
        player.show(hand_to_str(player.hand))


class Moat(ActionCard):
    def __init__(self):
        super().__init__(
            name="Moat",
            cost=2,
            desc="+2 cards. When another player plays an Attack card, you may first reveal this from your hand, to be unaffected by it.",
        )

    def play(self, game_ctx, player):
        events = [MoatEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


MOAT = Moat()
