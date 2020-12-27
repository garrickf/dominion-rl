"""Poacher: +1 card. +1 action. +(1). Discard a card per empty supply pile.
"""

# From dominion module
from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event, PlayActionEvent
from dominion.prettyprint import hand_to_str, options_to_str


def get_options(cards, already_chosen):
    # Any card can be discarded
    return {
        idx: card.name for idx, card in enumerate(cards) if idx not in already_chosen
    }


class PoacherEvent(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=1, replace_hand=False)
        num_empty_piles = 0
        for card in game_ctx.table:
            if game_ctx.table[card] == 0:
                num_empty_piles += 1

        are_str = "is" if num_empty_piles == 1 else "are"
        piles_str = "pile" if num_empty_piles == 1 else "piles"
        player.show(f"There {are_str} {num_empty_piles} empty supply {piles_str}")

        marked_for_discard = []
        player.show(hand_to_str(player.hand))
        while len(marked_for_discard) < num_empty_piles:
            options = get_options(player.hand, marked_for_discard)
            player.show(options_to_str(options))

            prompt_str = "Discard a card per empty supply pile"
            c = player.get_input(prompt_str, options, allow_skip=False)
            marked_for_discard.append(c)

        player.deck.move(
            marked_for_discard, from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD
        )


class Poacher(ActionCard):
    def __init__(self):
        super().__init__(
            name="Poacher",
            cost=4,
            desc="+1 card. +1 action. +(1). Discard a card per empty supply pile.",
        )

    def play(self, game_ctx, player):
        events = [PoacherEvent(target=player.name), PlayActionEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


POACHER = Poacher()
