"""Militia: +(2). Each other player discards down to three cards in hand.
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event
from dominion.prettyprint import card_to_str, cards_to_str, hand_to_str, options_to_str

from .moat import MOAT


def get_reaction_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card == MOAT:
            options[idx] = card
    return options


def get_discard_options(hand, already_discarded):
    # Any card can be discarded
    return {
        idx: card.name for idx, card in enumerate(hand) if idx not in already_discarded
    }


class MilitiaEventSelf(Event):
    def forward(self, game_ctx, player):
        player.set_modifier("extra_treasure", lambda v: v + 2)


class MilitiaEventOther(Event):
    def forward(self, game_ctx, player):
        if MOAT in player.hand:
            player.show(hand_to_str(player.hand))

            options = get_reaction_options(player.hand)
            prompt_str = (
                "You may reveal a Moat from your hand to be unaffected by this attack"
            )
            c = player.get_input(prompt_str, options, allow_skip=True)
            if c is not "Skip":
                card = player.hand[c]
                logging.log(
                    [logging.GAME, logging.OBSERVER],
                    f"{player.name} reveals a {card_to_str(card)}, defending themselves!",
                )
                return

        # Discard down to three cards in hand
        player.show(hand_to_str(player.hand))

        marked_for_discard = []
        while len(player.hand) - len(marked_for_discard) > 3:
            options = get_discard_options(player.hand, marked_for_discard)
            player.show(options_to_str(options))
            prompt_str = "Choose a card to discard"
            c = player.get_input(prompt_str, options, allow_skip=False)
            marked_for_discard.append(c)

        to_discard = [player.hand[c] for c in marked_for_discard]
        player.deck.move(to_discard, from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD)

        player.show(hand_to_str(player.hand))
        logging.log(
            logging.OBSERVER,
            f"{player.name} discarded {len(to_discard)} card{'' if len(to_discard) == 1 else 's'}",
        )
        logging.log(
            logging.GAME,
            f"{player.name} discarded {len(to_discard)} card{'' if len(to_discard) == 1 else 's'}: {cards_to_str(to_discard)}",
        )


class Militia(ActionCard):
    def __init__(self):
        super().__init__(
            name="Militia",
            cost=4,
            desc="+(2). Each other player discards down to three cards in hand.",
        )

    def play(self, game_ctx, player):
        events = [MilitiaEventSelf(target=player.name)]

        # TODO: clarify between player names and objects
        for other_player_name in game_ctx.get_other_players(player.name):
            events.append(MilitiaEventOther(target=other_player_name))

        game_ctx.add_events(events, where=QueuePosition.FRONT)


MILITIA = Militia()
