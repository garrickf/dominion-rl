# Intended usage: from dominion.cards.base_game import KINGDOM_CARDS, BASE_SET, etc.

from .artisan import ARTISAN
from .bureaucrat import BUREAUCRAT
from .copper import COPPER
from .curse import CURSE
from .duchy import DUCHY
from .estate import ESTATE
from .gardens import GARDENS
from .gold import GOLD
from .merchant import MERCHANT
from .militia import MILITIA
from .mine import MINE
from .moat import MOAT
from .moneylender import MONEYLENDER
from .province import PROVINCE
from .remodel import REMODEL
from .silver import SILVER
from .throne_room import THRONE_ROOM
from .village import VILLAGE
from .witch import WITCH
from .workshop import WORKSHOP

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
