"""A Deck is a player's collection of cards. This collection grows over the
course of the game as the player acquires more cards. Cards in the deck are
divided into three main piles: a draw pile, a discard pile, and the player's
hand. Basic operations are supplied to manipulate these piles (add, move, trash),
as well as methods to perform common operations during the game (draw_cards,
cleanup).
"""

# Python stdlib
import random  # For shuffle
from collections import defaultdict
from typing import Sequence, Union

# From dominion module
from dominion.cards import Card
from dominion.cards.base_game import STARTER_DECK
from dominion.common import DeckPile

Targets = Union[Sequence[Union[int, Card]], int, Card]


class Deck:
    def __init__(self, *, starter_deck=STARTER_DECK):
        """A Deck has a draw pile, discard pile, hand, a way to hold played cards
        during a turn, and a dict of card counts.
        """
        self.draw_pile = starter_deck
        random.shuffle(self.draw_pile)
        self.discard_pile = []
        self.hand = []
        self.played_cards = []
        self._update_counts()

    def __len__(self):
        """Returns the total number of cards in the deck."""
        return sum([v for v in self.counts.values()])

    def _reshuffle(self) -> None:
        """Helper method that shuffles the discard pile back into the draw
        pile.
        """
        random.shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []

    def _update_counts(self) -> None:
        """Helper that recounts all the cards in the player's possession. Used
        when cards are (1) trashed or (2) acquired via add().
        """
        self.counts = defaultdict(int)
        for card in self.draw_pile + self.discard_pile + self.hand + self.played_cards:
            self.counts[card] += 1

    def _discard_hand(self) -> None:
        """Helper (only used in Deck) to move cards in hand to discard pile."""
        self.discard_pile += self.hand
        self.hand = []

    def draw_cards(self, n: int, replace_hand: bool = True, to_caller: bool = False):
        """Draw n cards, optionally replacing (discarding) cards in hand. or
        returning cards directly.

        Args:
            n (int): The number of cards to draw.
            replace_hand (bool): Whether or not the draw will replace the player's
                hand. Defaults to True, which is the desired behavior when a player
                draws their hand for the next turn.
            to_caller (bool): If True, bypasses the hand and returns the cards
                that were drawn. Cards returned in this way can be manipulated,
                but must be added back to the Deck unless they are to be trashed.
        Returns:
            (list) The cards that were drawn
        """
        if not to_caller and replace_hand:
            self._discard_hand()

        # If draw pile is smaller than n, reshuffle
        if len(self.draw_pile) < n:
            self._reshuffle()

        drawn = self.draw_pile[:n]
        self.draw_pile = self.draw_pile[n:]

        # Return cards to caller if specified; otherwise, add to hand
        if to_caller:
            return drawn

        self.hand += drawn
        return self.hand

    def trash(self, cards: Targets, from_pile: DeckPile = DeckPile.HAND) -> None:
        """Remove a list of cards from a specified pile. Reduces overall deck
        counts.

        Currently only supports trashing from hand; any action cards in the base
        game that allow/require trashing only do trashing from hand.

        Args:
            cards: (list or int or Dominion.cards.Card): Accepts a list or
                single item. The item(s) must be indices into the from_pile, or
                Card objects. Card objects will be looked up and turned into
                indices.
            from_pile: (Dominion.common.DeckPile): The pile to trash cards from.
                Defaults to the hand.
        Returns:
            None
        Raises:
            RuntimeError: If any cards could not be found in from_pile
        """
        self.move(cards, from_pile=from_pile, to_pile=DeckPile.TRASH)
        self._update_counts()

    def cleanup(self) -> None:
        """Moves any cards in the played pile to the discard pile. Called when
        the player's turn ends.
        """
        self.discard_pile += self.played_cards
        self.played_cards = []

    def add(
        self, cards: Union[Sequence[Card], Card], to_pile: DeckPile = DeckPile.DISCARD
    ) -> None:
        """Add list of cards to a specified pile. Increases overall deck
        counts. If added to the draw pile, adds cards to the front (i.e.,
        the top of the pile). Otherwise, cards are added to the end.

        Args:
            cards: (list or Dominion.cards.Card): Accepts a list or
                single item. The item(s) must subclass Card.
            to_pile: (Dominion.common.DeckPile): The pile to add cards to.
        Returns:
            None
        """
        # If targets is an empty list
        if type(cards) is list and not cards:
            return

        if type(cards) is not list:
            _cards = [cards]
        else:
            _cards = cards

        if to_pile == DeckPile.DISCARD:
            self.discard_pile += _cards
        elif to_pile == DeckPile.HAND:
            self.hand += _cards
        elif to_pile == DeckPile.DRAW:
            # Add to top of draw pile
            self.draw_pile = _cards + self.draw_pile
        else:
            raise NotImplementedError("not implemented")
        self._update_counts()

    def move(
        self,
        targets: Targets,
        *,
        from_pile: DeckPile,
        to_pile: DeckPile,
        to_pos: str = "TOP",
    ) -> None:
        """Move list of cards from one pile to another. Preserves overall deck
        counts.

        Args:
            targets: (list or int or Dominion.cards.Card): Accepts a list or
                single item. The item(s) must be indices into the from_pile, or
                Card objects. Card objects will be looked up and turned into
                indices.
            from_pile: (Dominion.common.DeckPile): The pile to move cards from.
            to_pile: (Dominion.common.DeckPile): The pile to move cards to.
            to_pos: (str): One of "TOP" or "BOTTOM"; where in the pile to add
                cards.
        Returns:
            None
        Raises:
            RuntimeError: If any cards could not be found in from_pile
        """
        ENUM_TO_PILE = {
            DeckPile.DISCARD: self.discard_pile,
            DeckPile.DRAW: self.draw_pile,
            DeckPile.HAND: self.hand,
            DeckPile.PLAYED: self.played_cards,
            DeckPile.TRASH: [],
        }

        from_loc = ENUM_TO_PILE[from_pile]
        to_loc = ENUM_TO_PILE[to_pile]

        # If targets is an empty list
        if type(targets) is list and not targets:
            return

        if type(targets) is not list:
            _targets = [targets]
        else:
            _targets = targets

        if isinstance(_targets[0], int):
            target_idxs = _targets
        else:  # List of Cards
            target_idxs = []
            for idx, card in enumerate(from_loc):
                if card in _targets:
                    target_idxs.append(idx)
                    _targets.remove(card)

            # If target non-empty, all card idxs not found in from pile
            if _targets:
                raise RuntimeError("desired card not found in from_pile")

        new_from_loc = []
        moved = []
        for idx, card in enumerate(from_loc):
            if idx in target_idxs:
                moved.append(card)
            else:
                new_from_loc.append(card)

        # Change internal contents, not switch views
        from_loc[:] = new_from_loc

        if to_pos == "TOP":
            to_loc[:] = to_loc + moved
        elif to_pos == "BOTTOM":
            to_loc[:] = moved + to_loc
        else:
            raise NotImplementedError("not implemented")
