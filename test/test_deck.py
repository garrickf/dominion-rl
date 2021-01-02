# From dominion module
from dominion.cards.base_game import COPPER
from dominion.common import DeckPile
from dominion.players import Deck


def test_deck_init():
    # Create a new Deck
    deck = Deck()

    assert len(deck) == 10, "Starting deck size should be 10"
    assert len(deck.hand) == 0, "Starting hand should be empty"
    assert len(deck.discard_pile) == 0, "Starting discard pile should be empty"
    assert len(deck.draw_pile) == 10, "Starting draw pile size should be 10"


def test_deck_draw():
    # Draw a hand of 5 cards
    deck = Deck()
    hand = deck.draw_cards(n=5, replace_hand=True)

    assert len(hand) == 5, "Should draw hand of 5 cards"
    assert hand == deck.hand, "Hand should match deck.hand"
    assert len(deck) == 10, "Drawing cards should not affect deck size"

    # Draw a new hand, depleting the draw pile
    hand = deck.draw_cards(n=5, replace_hand=True)

    assert len(deck.discard_pile) == 5, "Should discard 5 cards on 2nd draw"
    assert len(hand) == 5, "Should draw hand of 5 cards"
    assert len(deck.draw_pile) == 0, "Draw pile should be emptied"

    # Draw 1 extra card, forcing a reshuffle
    hand = deck.draw_cards(n=1, replace_hand=False)

    assert len(hand) == 6, "Should get new hand of 6 cards"
    assert hand == deck.hand, "Hand should match deck.hand"
    assert len(deck) == 10, "Drawing cards should not affect deck size"
    assert len(deck.discard_pile) == 0, "Discard pile should be emptied"


def test_deck_trash():
    # Draw a hand of 5 cards, then trash a Copper from hand
    deck = Deck()
    hand = deck.draw_cards(n=5, replace_hand=True)
    deck.trash([COPPER])

    assert len(deck.hand) == 4, "Hand should have 4 cards"
    assert len(deck) == 9, "Deck should have 9 cards"


def test_deck_add():
    # Draw a hand of 5 cards, then add a Copper to the discard pile
    deck = Deck()
    hand = deck.draw_cards(n=5, replace_hand=True)
    deck.add([COPPER, COPPER])

    assert len(deck.hand) == 5, "Hand should have 5 cards"
    assert len(deck) == 12, "Deck should have 12 cards"
    assert len(deck.discard_pile) == 2, "Discard should have 2 new cards"


def test_deck_move():
    # Draw a hand of 5 cards, then move a Copper to the top of the discard pile
    deck = Deck()
    hand = deck.draw_cards(n=5, replace_hand=True)
    deck.move([COPPER], from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD)

    assert len(deck.hand) == 4, "Hand should have 4 cards"
    assert len(deck) == 10, "Deck should have 10 cards"
    assert len(deck.discard_pile) == 1, "Discard should have 1 new card"
    assert deck.discard_pile[0] == COPPER, "Copper should be at top of discard"
