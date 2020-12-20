# Intended usage: from dominion.cards.base_game import KINGDOM_CARDS, BASE_SET, etc.

from .copper import COPPER
from .curse import CURSE
from .duchy import DUCHY
from .estate import ESTATE
from .gardens import GARDENS
from .gold import GOLD
from .mine import MINE
from .province import PROVINCE
from .silver import SILVER
from .village import VILLAGE

KINGDOM_CARDS = [
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
    VILLAGE,
]

STARTER_DECK = [ESTATE] * 3 + [COPPER] * 7
