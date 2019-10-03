from numpy.random import choice

supply = [8, 8, 8, 46, 40, 30]
cost = [8, 5, 2, 6, 3, 0]
vp = [6, 3, 1, 0, 0, 0]
value = [0, 0, 0, 3, 2, 1]
deck = [0, 0, 3, 0, 0, 7]
discard = []
hand = [0,0,0,0,0,0]

def dot(v1, v2):
	return sum([v1[k] * v2[k] for k in range(len(v1))])

def drawCard(deck, hand):
	card = choice([0, 1, 2, 3, 4, 5], 1, p=[x/sum(deck) for x in deck])[0]
	hand[card] += 1
	deck[card] -= 1

def drawHand(deck, hand):
	for i in range(5):
		if sum(deck) == 0:
			deck = discard
			discard = [0 for i in range(5)]
		drawCard(deck, hand)

print("Money in deck: ", dot(deck, value))
print("VP in deck: ", dot(deck, vp))
print("Hand: ", hand, 'Deck: ', deck)
drawHand(deck, hand)
print("Hand: ", hand, 'Deck: ', deck)



# define a method to pick a random card out of the deck
# define a method to draw the hand

"""
class Player:
	def __init__(self)

player1 = Player()
"""
