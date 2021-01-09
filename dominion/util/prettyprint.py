from collections import defaultdict
from colorama import Fore, Back, Style
from dominion.common import CardType

# TODO: with dim style

TREASURE_TO_COLOR = {
    "Copper": Fore.RED,
    "Silver": Fore.WHITE,
    "Gold": Fore.YELLOW,
}

CARDTYPE_TO_COLOR = {
    CardType.VICTORY: Fore.GREEN,
    CardType.ACTION: Fore.CYAN,
    CardType.ACTION_ATTACK: Fore.CYAN,
    CardType.ACTION_REACTION: Fore.CYAN,
    CardType.CURSE: Fore.BLUE,
}


def card_to_str(card):
    color = Fore.WHITE
    if card.kind == CardType.TREASURE:
        color = TREASURE_TO_COLOR[card.name]
    else:
        color = CARDTYPE_TO_COLOR[card.kind]
    return "{}{}{}".format(color, str(card), Style.RESET_ALL)


def hand_to_str(hand):
    return cards_to_str(hand, header="Current hand")


def filter_treasures_as_str(cards):
    counts = defaultdict(int)
    for card in cards:
        if card.kind == CardType.TREASURE:
            counts[card] += 1
    return ", ".join(
        ["{} {}".format(counts[card], card_to_str(card)) for card in counts]
    )


def deck_to_str(deck):
    s = "Deck:\n"
    for i, (card, v) in enumerate(deck.counts.items()):
        if i % 3 == 0 and i > 0:
            s += "\n"
        s += "[{:>2}] {!s:<23}".format(v, card_to_str(card))
    return s + "\n"


# TODO: method for string player name, numbered choices, etc.


def options_to_str(options):
    # TODO: allow card like formatting, or allow including descriptions from supply/hand
    s = "Options:\n"
    for c, card_string in options.items():
        s += f"{c}. {card_string}\n"
    return s + "\n"


def cards_to_str(cards, header="Cards"):
    s = f"{header}:\n"
    for idx, card in enumerate(cards):
        s += "{}. {}\n".format(idx, card_to_str(card))
    return s


def supply_to_str(supply, max_line_len=100):
    s = "Supply:\n"
    s += "{:<4}{:<16}{:<5}{:<7}{:<}\n".format("", "Name", "Left", "Cost", "Description")
    for i, (card, left) in enumerate(supply.items()):
        line = "{:>2}. {!s:<24} [{:>2}] ({:>2}) | {}\n".format(
            i, card_to_str(card), left, card.cost, card.desc
        )
        if len(line) > max_line_len:
            remainder = line
            new_lines = []
            while len(remainder) > max_line_len:
                split_point = remainder.find(" ", max_line_len)
                if split_point == -1:
                    break
                new_line = remainder[:split_point] + "\n"
                new_lines.append(new_line)

                remainder = "{:<34}{}".format("", remainder[split_point:])

            new_lines.append(remainder)
            line = "".join(new_lines)
        s += line
    return s
