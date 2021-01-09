""" Witch: +2 cards. Each other player gains a Curse.
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionAttackCard
from dominion.common import QueuePosition
from dominion.events import Event
from dominion.util.prettyprint import card_to_str, hand_to_str

from .curse import CURSE
from .moat import MOAT


def get_reaction_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card == MOAT:
            options[idx] = card.name
    return options


class WitchEventSelf(Event):
    def forward(self, game_ctx, player):
        player.deck.draw_cards(n=2, replace_hand=False)
        player.show(hand_to_str(player.hand))


class WitchEventOther(Event):
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

        # Player gains a curse, if there are still curses
        if game_ctx.supply[CURSE] > 0:
            game_ctx.supply.buy(CURSE, player, free=True)
            logging.log(
                [logging.GAME, logging.OBSERVER],
                f"{player.name} gains a {card_to_str(CURSE)}",
            )
        else:
            logging.log(
                [logging.GAME, logging.OBSERVER],
                f"{player.name} does not gain a {card_to_str(CURSE)}, as there are no more in the Supply. Phew!",
            )


# TODO: action/attack card
class Witch(ActionAttackCard):
    def __init__(self):
        super().__init__(
            name="Witch", cost=5, desc="+2 cards. Each other player gains a Curse."
        )

    def play(self, game_ctx, player):
        events = [WitchEventSelf(target=player.name)]

        # TODO: clarify between player names and objects
        for other_player_name in game_ctx.get_other_players(player.name):
            events.append(WitchEventOther(target=other_player_name))

        game_ctx.add_events(events, where=QueuePosition.FRONT)


WITCH = Witch()
