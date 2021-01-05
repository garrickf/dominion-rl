import pytest

# From dominion module
from dominion.cards.base_game import COPPER, SILVER, VILLAGE
from dominion.common import DeckPile
from dominion.players import Deck


def test_deck_init():
    # Create a new Deck
    deck = Deck()

    assert len(deck) == 10, "Starting deck size should be 10"
    assert len(deck.hand) == 0, "Starting hand should be empty"
    assert len(deck.discard_pile) == 0, "Starting discard pile should be empty"
    assert len(deck.draw_pile) == 10, "Starting draw pile size should be 10"


def test_draw():
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


def test_trash():
    # Draw a hand of 5 cards, then trash a Copper from hand
    deck = Deck()
    deck.draw_cards(n=5, replace_hand=True)
    deck.trash(COPPER)

    assert len(deck.hand) == 4, "Hand should have 4 cards"
    assert len(deck) == 9, "Deck should have 9 cards"


def test_trash_indexed():
    # Draw a hand of 5 cards, then trash cards 0, 1 from hand
    deck = Deck()
    deck.draw_cards(n=5, replace_hand=True)
    deck.trash([0, 1])

    assert len(deck.hand) == 3, "Hand should have 3 cards"
    assert len(deck) == 8, "Deck should have 8 cards"


def test_add():
    # Draw a hand of 5 cards, then add a Copper to the discard pile
    deck = Deck()
    deck.draw_cards(n=5, replace_hand=True)
    deck.add([COPPER, COPPER])

    assert len(deck.hand) == 5, "Hand should have 5 cards"
    assert len(deck) == 12, "Deck should have 12 cards"
    assert len(deck.discard_pile) == 2, "Discard should have 2 new cards"


def test_move():
    # Draw a hand of 5 cards, then move a Copper to the top of the discard pile
    deck = Deck()
    deck.draw_cards(n=5, replace_hand=True)
    deck.move(COPPER, from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD)

    assert len(deck.hand) == 4, "Hand should have 4 cards"
    assert len(deck) == 10, "Deck should have 10 cards"
    assert len(deck.discard_pile) == 1, "Discard should have 1 new card"
    assert deck.discard_pile[0] == COPPER, "Copper should be at top of discard"


def test_move_indexed():
    # Draw a hand of 5 cards, then move cards 2, 3, 4 to the top of the discard pile
    deck = Deck()
    deck.draw_cards(n=5, replace_hand=True)
    deck.move([2, 3, 4], from_pile=DeckPile.HAND, to_pile=DeckPile.DISCARD)

    assert len(deck.hand) == 2, "Hand should have 2 cards"
    assert len(deck) == 10, "Deck should have 10 cards"
    assert len(deck.discard_pile) == 3, "Discard should have 3 new cards"


def test_move_card_not_found():
    # Draw a hand of 5 cards, then attempt to move a Silver
    deck = Deck()
    deck.draw_cards(5)
    with pytest.raises(RuntimeError):
        deck.move(SILVER, from_pile=DeckPile.HAND, to_pile=DeckPile.DRAW)


def test_draw_to_caller():
    # Draw 3 cards to the caller, removing them temporarily from the deck
    deck = Deck()
    cards = deck.draw_cards(3, to_caller=True)

    assert len(cards) == 3, "There should be 3 drawn cards"
    assert len(deck) == 7, "Deck should have 7 cards"

    # Add one card back
    cards = cards[:1]
    deck.add(cards)
    assert len(deck) == 8, "Deck should have 8 cards"


def test_cleanup():
    # Draw cards to hand, move them to played, then cleanup, moving played cards
    # to discard
    deck = Deck(starter_deck=[VILLAGE, VILLAGE])
    deck.draw_cards(2)
    deck.move([VILLAGE] * 2, from_pile=DeckPile.HAND, to_pile=DeckPile.PLAYED)

    assert len(deck) == 2, "Deck should have 2 cards"
    assert len(deck.played_cards) == 2, "Deck should have 2 played cards"
    assert len(deck.discard_pile) == 0, "Discard pile should be empty"

    deck.cleanup()
    assert len(deck) == 2, "Deck should have 2 cards"
    assert len(deck.discard_pile) == 2, "Discard pile should have 2 cards"
    assert len(deck.played_cards) == 0, "Deck should have no played cards"


def test_move_empty():
    # Move nothing, nothing should happen
    deck = Deck()
    deck.draw_cards(5)

    deck.move([], from_pile=DeckPile.HAND, to_pile=DeckPile.TRASH)
    assert len(deck.hand) == 5, "Should have hand of 5 cards"
    assert len(deck) == 10, "Should have deck of 10 cards"
