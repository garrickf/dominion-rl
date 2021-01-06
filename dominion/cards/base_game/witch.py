""" Witch TODO: docstring
"""

from dominion.cards import ActionCard
from dominion.common import QueuePosition
from dominion.events import Event
from dominion.prettyprint import card_to_str, hand_to_str

from .curse import CURSE
from .moat import MOAT


def get_reaction_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card == MOAT:
            options[idx] = card
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
                print(f"Player reveals a {card_to_str(card)}, defending themselves!")
                return

        # Player gains a curse, if there are still curses
        if game_ctx.supply[CURSE] > 0:
            game_ctx.supply.buy(CURSE, player, free=True)
            print(f"Player gains a {card_to_str(CURSE)}")
        else:
            print("No curses left, phew!")  # TODO: refine


# TODO: action/attack card
class Witch(ActionCard):
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
