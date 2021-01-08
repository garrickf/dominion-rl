"""Cellar: Discard any number of cards, then draw that many.
"""

# From dominion module
from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event
from dominion.util.prettyprint import hand_to_str


# TODO: create helper already selected function
def get_discard_options(hand, already_discarded):
    # Any card can be discarded
    return {
        idx: card.name for idx, card in enumerate(hand) if idx not in already_discarded
    }


class CellarEvent(Event):
    def forward(self, game_ctx, player):
        player.show(hand_to_str(player.hand))

        marked_for_discard = []
        while len(marked_for_discard) < len(player.hand):
            options = get_discard_options(player.hand, marked_for_discard)
            prompt_str = "You may discard a card from your hand"
            c = player.get_input(prompt_str, options, allow_skip=True)
            if c == "Skip":
                break

            marked_for_discard.append(c)

        # Discard cards, then draw
        player.deck.move(
            marked_for_discard, from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD
        )
        player.deck.draw_cards(n=len(marked_for_discard), replace_hand=False)
        player.show(hand_to_str(player.hand))


class Cellar(ActionCard):
    def __init__(self):
        super().__init__(
            name="Cellar",
            cost=2,
            desc="Discard any number of cards, then draw that many.",
        )

    def play(self, game_ctx, player):
        events = [CellarEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


CELLAR = Cellar()
