"""Chapel: Trash up to four cards from your hand.
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition, DeckPile
from dominion.events import Event, get_all_as_options


class ChapelEvent(Event):
    def forward(self, game_ctx, player):
        for i in range(4):
            options = get_all_as_options(player.hand)
            prompt_str = "Choose a card to trash ({}/4)".format(i + 1)
            c = player.get_input(prompt_str, options, allow_skip=True)

            if c == "Skip":
                break

            card = player.hand[c]
            player.deck.trash([card], from_pile=DeckPile.HAND)


class Chapel(ActionCard):
    def __init__(self):
        super().__init__(
            name="Chapel", cost=2, desc="Trash up to four cards from your hand."
        )

    def play(self, game_ctx, player):
        events = [
            ChapelEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


CHAPEL = Chapel()
