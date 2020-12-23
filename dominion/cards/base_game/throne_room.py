"""Throne Room: You may play an action card from your hand twice.
"""

from dominion.cards import ActionCard
from dominion.common import CardType, DeckPile, QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import card_to_str, hand_to_str, options_to_str


def get_actions_as_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card.kind in [
            CardType.ACTION,
            CardType.ACTION_ATTACK,
            CardType.ACTION_REACTION,
        ]:
            options[idx] = card.name

    return options


class ThroneRoomEvent(Event):
    def forward(self, game_ctx, player):
        player.show(hand_to_str(player.hand))

        options = get_actions_as_options(player.hand)
        if not options:
            player.show("No actions are available to play.\n")
            # If there are any other Events like this one, clear them
            clear_events_ahead_of_self(game_ctx, self)
            return

        prompt_str = "Choose an action to play twice"
        c = player.get_input(prompt_str, options, allow_skip=True)
        if c == "Skip":
            return

        action_card = player.hand[c]
        for _ in range(2):
            action_card.play(game_ctx, player)
        player.deck.move(
            [action_card], from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD
        )

        print(f"Player plays {card_to_str(action_card)} twice")


class ThroneRoom(ActionCard):
    def __init__(self):
        super().__init__(
            name="Throne Room",
            cost=4,
            desc="You may play an action card from your hand twice.",
        )

    def play(self, game_ctx, player):
        events = [ThroneRoomEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


THRONE_ROOM = ThroneRoom()
