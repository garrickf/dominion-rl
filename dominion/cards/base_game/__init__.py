# Intended usage: from dominion.cards.base_game import KINGDOM_CARDS, SILVER, etc.

# Python stdlib
from typing import List, Tuple

from ..card import Card
from .artisan import ARTISAN
from .bandit import BANDIT
from .bureaucrat import BUREAUCRAT
from .cellar import CELLAR
from .chapel import CHAPEL
from .copper import COPPER
from .council_room import COUNCIL_ROOM
from .curse import CURSE
from .duchy import DUCHY
from .estate import ESTATE
from .festival import FESTIVAL
from .gardens import GARDENS
from .gold import GOLD
from .harbinger import HARBINGER
from .laboratory import LABORATORY
from .library import LIBRARY
from .market import MARKET
from .merchant import MERCHANT
from .militia import MILITIA
from .mine import MINE
from .moat import MOAT
from .moneylender import MONEYLENDER
from .poacher import POACHER
from .province import PROVINCE
from .remodel import REMODEL
from .sentry import SENTRY
from .silver import SILVER
from .smithy import SMITHY
from .throne_room import THRONE_ROOM
from .vassal import VASSAL
from .village import VILLAGE
from .witch import WITCH
from .workshop import WORKSHOP

# All possible kingdom cards
KINGDOM_CARDS: List[Card] = [
    ARTISAN,
    BANDIT,
    BUREAUCRAT,
    CELLAR,
    CHAPEL,
    COUNCIL_ROOM,
    FESTIVAL,
    GARDENS,
    HARBINGER,
    LABORATORY,
    LIBRARY,
    MARKET,
    MERCHANT,
    MILITIA,
    MINE,
    MOAT,
    MONEYLENDER,
    POACHER,
    REMODEL,
    SENTRY,
    SMITHY,
    THRONE_ROOM,
    VASSAL,
    VILLAGE,
    WITCH,
    WORKSHOP,
]

# Starting deck configuration
STARTER_DECK: Tuple[Card, ...] = (ESTATE,) * 3 + (COPPER,) * 7
