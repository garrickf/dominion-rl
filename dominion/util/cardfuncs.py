"""Functions for operating with Dominion cards (checking if a card is an action,
filtering cards by certain properties, etc.)
"""

from dominion.cards import Card
from dominion.common import CardType

# TODO: add stuff
def is_action_card(card: Card) -> bool:
    """ Returns whether the passed in card is an action or not.
    """
    return card.kind in [
        CardType.ACTION,
        CardType.ACTION_ATTACK,
        CardType.ACTION_REACTION,
    ]
