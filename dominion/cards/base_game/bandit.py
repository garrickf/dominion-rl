"""Bandit: Gain a Gold. Each other player reveals the top 2 cards of their deck,
trashes a revealed treasure other than Copper, and discards the rest.
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionCard
from dominion.common import DeckPile, QueuePosition
from dominion.events import Event
from dominion.prettyprint import card_to_str, cards_to_str, options_to_str, hand_to_str

from .gold import GOLD
from .silver import SILVER
from .moat import MOAT


def get_reaction_options(hand):
    options = {}
    for idx, card in enumerate(hand):
        if card == MOAT:
            options[idx] = card
    return options


def get_treasures_as_options(cards):
    """Takes a list of cards and returns a dict from index to string option"""
    options = {}
    for idx, card in enumerate(cards):
        if card in [GOLD, SILVER]:
            options[idx] = card.name
    return options


class BanditEventSelf(Event):
    def forward(self, game_ctx, player):
        if game_ctx.supply[GOLD] > 0:
            game_ctx.supply.buy(GOLD, player, free=True, to_pile=DeckPile.DISCARD)
            logging.log(
                [logging.GAME, logging.OBSERVER],
                f"{player.name} acquired a {card_to_str(GOLD)}",
            )
        else:
            player.show("There are no more Golds in the Supply.")
            logging.log(
                [logging.GAME, logging.OBSERVER],
                f"{player.name} cannot acquire a a {card_to_str(GOLD)}, as there are no more in the Supply.",
            )


class BanditEventOther(Event):
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

        top_cards = player.deck.draw_cards(n=2, to_caller=True)
        logging.log(
            [logging.GAME, logging.OBSERVER],
            f"{player.name} reveals top two cards: {cards_to_str(top_cards)}",
        )

        if any(treasure in top_cards for treasure in [GOLD, SILVER]):
            options = get_treasures_as_options(top_cards)
            player.show(options_to_str(options))
            prompt_str = "You must trash a treasure other than Copper"
            c = player.get_input(prompt_str, options, allow_skip=False)

            # By not adding the card to discard, it's implicitly trashed.
            # Add will update counts
            del top_cards[c]
            logging.log(
                [logging.GAME, logging.OBSERVER],
                f"{player.name} trashes {options[c]}",
            )

        player.deck.add(top_cards, to_pile=DeckPile.DISCARD)


# TODO: subclass as ActionAttackCard
class Bandit(ActionCard):
    def __init__(self):
        super().__init__(
            name="Bandit",
            cost=5,
            desc=(
                "Gain a Gold. Each other player reveals the top 2 cards of their"
                " deck, trashes a revealed treasure other than Copper, and"
                " discards the rest."
            ),
        )

    def play(self, game_ctx, player):
        events = [BanditEventSelf(target=player.name)]

        # TODO: clarify between player names and objects
        for other_player_name in game_ctx.get_other_players(player.name):
            events.append(BanditEventOther(target=other_player_name))

        game_ctx.add_events(events, where=QueuePosition.FRONT)


BANDIT = Bandit()
