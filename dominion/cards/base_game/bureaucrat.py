"""Bureaucrat: Gain a Silver onto your deck. Each other player reveals a 
Victory card from their hand and puts it onto their deck (or reveals a hand with 
no Victory cards).
"""

from dominion.cards import ActionCard
from dominion.common import CardType, DeckPile, QueuePosition
from dominion.events import Event, clear_events_ahead_of_self
from dominion.prettyprint import card_to_str, hand_to_str, options_to_str

from .moat import MOAT
from .silver import SILVER


def get_reaction_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card == MOAT:
            options[idx] = card
    return options


def get_victory_card_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card.kind == CardType.VICTORY:
            options[idx] = card
    return options


class BureaucratEventSelf(Event):
    def forward(self, game_ctx, player):
        if game_ctx.table[SILVER] > 0:
            game_ctx.table.buy(SILVER, player, free=True, to_pile=DeckPile.DRAW)
            print(f"Player acquired a {card_to_str(SILVER)}")
        else:
            player.show("There are no more Silvers on the table.")


class BureaucratEventOther(Event):
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

        # Player must reveal a Victory card, or a hand with no Victory cards
        player.show(hand_to_str(player.hand))
        options = get_victory_card_options(player.hand)

        if not options:
            print("Player reveals hand, with no Victory cards!\n")
            print(hand_to_str(player.hand))
        else:
            prompt_str = (
                "Reveal a Victory card from your hand and put it onto your deck"
            )
            c = player.get_input(prompt_str, options, allow_skip=False)
            card = player.hand[c]
            print(
                f"Player reveals a {card_to_str(card)} and places it on top of their deck"
            )
            player.deck.move([card], from_pile=DeckPile.HAND, to_pile=DeckPile.DRAW)


# TODO: action/attack card
class Bureaucrat(ActionCard):
    def __init__(self):
        super().__init__(
            name="Bureaucrat",
            cost=4,
            desc="Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it onto their deck (or reveals a hand with no Victory cards).",
        )

    def play(self, game_ctx, player):
        events = [BureaucratEventSelf(target=player.name)]

        # TODO: clarify between player names and objects
        for other_player_name in game_ctx.get_other_players(player.name):
            events.append(BureaucratEventOther(target=other_player_name))

        game_ctx.add_events(events, where=QueuePosition.FRONT)


BUREAUCRAT = Bureaucrat()
