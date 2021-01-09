"""Library: Draw until you have 7 cards in hand, skipping any action cards you 
choose to; set those aside, discarding them afterwards.
"""

# From dominion module
from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event
from dominion.util.cardfuncs import is_action_card
from dominion.util.prettyprint import hand_to_str, options_to_str


class LibraryEvent(Event):
    def forward(self, game_ctx, player):
        while len(player.hand) < 7:
            next_card = player.deck.draw_cards(n=1, to_caller=True)[0]
            if is_action_card(next_card):
                options = {1: next_card.name}
                player.show(options_to_str(options))
                prompt_str = "You may add this card to your hand"
                c = player.get_input(prompt_str, options, allow_skip=True)
                if c == "Skip":
                    # Add to discard
                    player.deck.add([next_card], to_pile=DeckPile.DISCARD)

            player.deck.add([next_card], to_pile=DeckPile.HAND)

        player.show(hand_to_str(player.hand))


class Library(ActionCard):
    def __init__(self):
        super().__init__(
            name="Library",
            cost=5,
            desc=(
                "Draw until you have 7 cards in hand, skipping any action cards"
                " you choose to; set those aside, discarding them afterwards."
            ),
        )

    def play(self, game_ctx, player):
        events = [LibraryEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


LIBRARY = Library()
