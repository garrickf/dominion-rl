""" Pretty printing functions TODO: docstring
"""

from colorama import Fore, Back, Style
from dominion.common import CardType

TREASURE_TO_COLOR = {
    'Copper': Fore.RED,
    'Silver': Fore.WHITE,
    'Gold': Fore.YELLOW,
}

CARDTYPE_TO_COLOR = {
    CardType.VICTORY: Fore.GREEN,
    CardType.ACTION: Fore.CYAN,
    CardType.CURSE: Fore.BLUE,
}


def card_to_str(card):
    color = Fore.WHITE
    if card.kind == CardType.TREASURE:
        color = TREASURE_TO_COLOR[card.name]
    else:
        color = CARDTYPE_TO_COLOR[card.kind]
    return '{}{}{}'.format(color, str(card), Style.RESET_ALL)


def hand_to_str(hand):
    s = 'Current hand:\n'
    for idx, card in enumerate(hand):
        s += '{}. {}\n'.format(idx, card_to_str(card))
    return s


def deck_to_str(deck):
    s = "Deck:\n"
    for i, (card, v) in enumerate(deck.counts.items()):
        if i % 3 == 0 and i > 0:
            s += '\n'
        s += '[{:>2}] {!s:<23}'.format(v, card_to_str(card))
    return s + '\n'

# TODO: method for string player name, numbered choices, etc.
