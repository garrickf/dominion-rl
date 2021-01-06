""" Artisan: Gain a card to your hand costing up to (5). Put a card from 
your hand onto your deck.
"""

from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import card_to_str, hand_to_str, options_to_str


def get_buy_options(supply):
    value = 5
    options = {}
    for idx, card in enumerate(supply):
        left = supply[card]
        if card.cost <= value and left > 0:
            options[idx] = card.name
    return options


def get_place_options(hand):
    # Any card can be put on top of the deck
    return {idx: card.name for idx, card in enumerate(hand)}


class ArtisanEvent(Event):
    def forward(self, game_ctx, player):
        options = get_buy_options(game_ctx.supply)

        if not options:
            player.show("No cards are available to get.\n")
            # If there are any other Events like this one, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        player.show(options_to_str(options))
        prompt_str = "Gain a card costing up to (5)"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        card = game_ctx.supply.buy(c, player, free=True, to_pile=DeckPile.HAND)
        print("Player acquired {}\n".format(card_to_str(card)))

        player.show(hand_to_str(player.hand))
        options = get_place_options(player.hand)
        prompt_str = "Put a card from your hand onto your deck"
        c = player.get_input(prompt_str, options, allow_skip=False)

        card = player.hand[c]
        player.deck.move([card], from_pile=DeckPile.HAND, to_pile=DeckPile.DRAW)

        print("Player moved a card from their hand to their deck")


class Artisan(ActionCard):
    def __init__(self):
        super().__init__(
            name="Artisan",
            cost=6,
            desc="Gain a card to your hand costing up to (5). Put a card from your hand onto your deck.",
        )

    def play(self, game_ctx, player):
        events = [ArtisanEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


ARTISAN = Artisan()
