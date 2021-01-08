"""Common Enum types used throughout Dominion."""

# Python stdlib
from enum import Enum, auto


class QueuePosition(Enum):
    BACK = auto()
    FRONT = auto()
    AFTER_NEXT = auto()
    BEFORE_NEXT_BUY = auto()


class CardType(Enum):
    VICTORY = auto()
    TREASURE = auto()
    ACTION = auto()
    ACTION_ATTACK = auto()
    ACTION_REACTION = auto()
    CURSE = auto()


class DeckPile(Enum):
    DRAW = auto()
    DISCARD = auto()
    HAND = auto()
    PLAYED = auto()
    TRASH = auto()


class PlayerType(Enum):
    HUMAN = auto()
    COMPUTER = auto()


class LogTarget(Enum):
    OBSERVER = auto()
    GAME = auto()
