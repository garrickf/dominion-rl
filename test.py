from card import *
from deck import Deck
from store import Store

stores = [
    Store(GOLD),
    Store(SILVER),
    Store(COPPER),
    Store(PROVINCE),
    Store(DUTCHY),
    Store(ESTATE)
]

for store in stores:
    print(store)

treasures = 4
num_buys = 1
print('can buy:', stores[0].can_buy(treasures, num_buys))
print('can buy:', stores[2].can_buy(treasures, num_buys))

# In order to do a game, you need:
# 10 piles of cards with initial size
# Player's decks to be initialized
# Player's hands to be initialized
# Action phase
# Let's say treasures are all autoplayed
# Buy
# Cleanup
# Draw