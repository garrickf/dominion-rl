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