# Intended usage: from dominion.cards.base_game import KINGDOM_CARDS, BASE_SET, etc.

from .copper import COPPER
from .silver import SILVER
from .gold import GOLD
from .estate import ESTATE
from .duchy import DUCHY
from .province import PROVINCE
from .gardens import GARDENS
from .curse import CURSE
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
