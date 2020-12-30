"""Harbinger: +1 card. +1 action. Look through your discard pile. You may put a 
card from it onto your deck.
"""

# From dominion module
from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event, PlayActionEvent
from dominion.prettyprint import cards_to_str


class HarbingerEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)
        player.show(cards_to_str(player.deck.discard_pile, header="Discard pile"))
        options = {i: card.name for i, card in enumerate(player.deck.discard_pile)}

        if not options:
            player.show("Discard pile is empty")
            return

        prompt_str = "You may put a card from your discard pile onto your deck"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        player.deck.move(c, from_pile=DeckPile.DISCARD, to_pile=DeckPile.DRAW)


class Harbinger(ActionCard):
    def __init__(self):
        super().__init__(
            name="Harbinger",
            cost=3,
            desc=(
                "+1 card. +1 action. Look through your discard pile. You may"
                " put a card from it onto your deck."
            ),
        )

    def play(self, game_ctx, player):
        events = [
            HarbingerEvent(target=player.name),
            PlayActionEvent(target=player.name),
        ]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


HARBINGER = Harbinger()
