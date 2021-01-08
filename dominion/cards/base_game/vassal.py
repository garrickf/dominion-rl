"""Vassal: +(2). Discard the top card of your deck. If it's an action, you may 
play it.
"""

# From dominion module
import dominion.util.logging as logging
from dominion.cards import ActionCard
from dominion.common import CardType, DeckPile, QueuePosition
from dominion.events import Event
from dominion.prettyprint import card_to_str, options_to_str


class VassalEvent(Event):
    def forward(self, game_ctx, player):
        player.set_modifier("extra_treasure", lambda v: v + 2)

        top_card = player.deck.draw_cards(n=1, to_caller=True)[0]
        if top_card.kind in [
            CardType.ACTION,
            CardType.ACTION,
            CardType.ACTION_REACTION,
        ]:
            options = {1: top_card.name}
            player.show(options_to_str(options))
            prompt_str = "You may play the action"
            c = player.get_input(prompt_str, options, allow_skip=True)
            if c == "Skip":
                return

            logging.log(
                [logging.OBSERVER, logging.GAME],
                f"{player.name} plays the top card of their deck, {card_to_str(top_card)}.",
            )
            top_card.play(game_ctx, player)

        # TODO: test more thoroughly
        player.deck.add([top_card], to_pile=DeckPile.DISCARD)
        logging.log(
            logging.OBSERVER,
            f"{player.name} discards the top card of their deck.",
        )

        logging.log(
            logging.GAME,
            f"{player.name} discards the top card of their deck, {card_to_str(top_card)}.",
        )


class Vassal(ActionCard):
    def __init__(self):
        super().__init__(
            name="Vassal",
            cost=3,
            desc="+(2). Discard the top card of your deck. If it's an action, you may play it.",
        )

    def play(self, game_ctx, player):
        events = [VassalEvent(target=player.name)]
        game_ctx.add_events(events, where=QueuePosition.FRONT)


VASSAL = Vassal()
