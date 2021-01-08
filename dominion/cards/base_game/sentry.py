"""Sentry: +1 card. +1 action. Look at the top 2 cards of your deck. Trash 
and/or discard any number of them. Put the rest back on top in any order.
"""

from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event, PlayActionEvent
from dominion.util.prettyprint import cards_to_str


def get_options(cards, already_chosen):
    # Any card can be discarded
    return {
        idx: card.name for idx, card in enumerate(cards) if idx not in already_chosen
    }


class SentryEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)

        # Look at the top 2 cards of your deck
        cards = player.deck.draw_cards(n=2, to_caller=True)
        player.show(cards_to_str(cards))

        marked_for_trash = []
        while len(cards) - len(marked_for_trash) > 0:
            options = get_options(cards, marked_for_trash)
            prompt_str = "Trash any number of cards"
            c = player.get_input(prompt_str, options, allow_skip=True)
            if c == "Skip":
                break
            else:
                marked_for_trash.append(c)

        cards = [card for idx, card in enumerate(cards) if idx not in marked_for_trash]
        # Not added back to deck -> automatically trashed

        if cards:
            player.show(cards_to_str(cards, header="After trashing"))

        marked_for_discard = []
        while len(cards) - len(marked_for_discard) > 0:
            options = get_options(cards, marked_for_discard)
            prompt_str = "Discard any number of cards"
            c = player.get_input(prompt_str, options, allow_skip=True)
            if c == "Skip":
                break
            else:
                marked_for_discard.append(c)

        to_discard = [cards[c] for c in marked_for_discard]
        cards = [
            card for idx, card in enumerate(cards) if idx not in marked_for_discard
        ]
        player.deck.add(to_discard, to_pile=DeckPile.DISCARD)

        if cards:
            player.show(cards_to_str(cards, header="After discarding"))

        if len(cards) > 1:
            options = {idx: card.name for idx, card in enumerate(cards)}
            prompt_str = "Choose first card to put back on draw pile"
            c = player.get_input(prompt_str, options, allow_skip=False)

            card = cards.pop(c)
            player.deck.add([card], to_pile=DeckPile.DRAW)

        player.deck.add(cards, to_pile=DeckPile.DRAW)


class Sentry(ActionCard):
    def __init__(self):
        super().__init__(
            name="Sentry",
            cost=5,
            desc=(
                "+1 card. +1 action. Look at the top 2 cards of your deck. Trash"
                " and/or discard any number of them. Put the rest back on top in"
                " any order."
            ),
        )

    def play(self, game_ctx, player):
        events = [SentryEvent(target=player.name), PlayActionEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


SENTRY = Sentry()
