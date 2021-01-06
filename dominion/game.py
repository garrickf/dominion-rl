"""The main Dominion game object, managing players, the event queue, and win 
conditions.
"""

# Python stdlib
from typing import Sequence, Tuple

import numpy as np

# From dominion module
import dominion.events as events
from dominion.cards.base_game import PROVINCE
from dominion.common import *
from dominion.players import ComputerPlayer, HumanPlayer, Player
from dominion.policy import RandomPolicy
from dominion.supply import Supply


# Game context stores order for players
class GameContext:
    def __init__(self, players=None) -> None:
        self.setup = False
        if players:
            self.player_order = players
            self._setup()

    def set_players(self, players: Sequence[Player]) -> None:
        self.player_order = players
        self._setup()

    def _setup(self) -> None:
        self.event_queue = []
        self.supply = Supply(n_players=len(self.player_order))
        self.turn = 0
        self.setup = True
        # On GameContext creation, scramble player order and create setup events

        for player in self.player_order:
            self.add_event(events.SetupEvent(target=player.name))

    def add_event(self, event, where=QueuePosition.BACK) -> None:
        """Adds a single event to the queue."""
        if where == QueuePosition.BACK:
            self.event_queue.append(event)
        elif where == QueuePosition.FRONT:
            self.event_queue.insert(0, event)

    def add_events(self, events, where=QueuePosition.BACK) -> None:
        """Adds a list of events to the queue."""
        if where == QueuePosition.BACK:
            self.event_queue = self.event_queue + events
        elif where == QueuePosition.FRONT:
            self.event_queue = events + self.event_queue

    def get_next_event(self):
        # Create new turns if event queue empty
        if not self.event_queue:
            self.turn += 1
            for player in self.player_order:
                self.add_event(events.PlayActionEvent(target=player.name))
                self.add_event(events.BuyEvent(target=player.name))
                self.add_event(events.CleanupEvent(target=player.name))

        return self.event_queue.pop(0)

    def get_other_players(self, cur_player_name: str):
        """Goes around the circle of player_order, returning all other players"""
        player_names = [player.name for player in self.player_order]
        idx = player_names.index(cur_player_name)
        other_players = player_names[idx + 1 :] + player_names[:idx]
        return other_players

    def reached_end(self) -> bool:
        """Returns true if the end of the game is reached. This can happen when:
        - There are no more Provinces
        - 3 piles are empty (4 in a four player game)
        """
        if self.supply[PROVINCE] == 0:
            return True

        n_piles_empty = len([v for v in self.supply.values() if v == 0])
        if n_piles_empty >= 3:
            return True

        return False

    def get_raw_state(self):
        """Returns the raw state of the game: whose turn it is, what cards are 
        in the supply, etc.
        """
        return {"state": []}


class Game:
    """Game objects manage a GameContext and multiple Controllers."""

    def __init__(self) -> None:
        # Create GameContext
        self.ctx = GameContext()

        # Initialize players
        players = []
        player_types = [PlayerType.COMPUTER, PlayerType.COMPUTER]
        for idx, player_type in enumerate(player_types):
            if player_type == PlayerType.HUMAN:
                player_name = f"Player {idx + 1}"
                player = HumanPlayer(player_name)
            else:  # Computer
                player_name = f"Player {idx + 1} (CPU)"
                player = ComputerPlayer(
                    player_name, RandomPolicy()
                )
                # player = ComputerPlayer(
                #     player_name, QLearningPolicy(raw_state_cb=self.ctx.get_raw_state)
                # )
            players.append(player)

        self.name_to_player = {player.name: player for player in players}

        # Add players to GameContext
        self.ctx.set_players(players)

    def play(self) -> Tuple[int, Sequence[int]]:
        # While game not finished
        # Get next event from queue
        # Run event forward with game context, relevant player
        if not self.ctx.setup:
            raise RuntimeError("game context not set up")

        while not self.ctx.reached_end():
            event = self.ctx.get_next_event()
            # Get player and controller
            player = self.name_to_player[event.target]
            event(self.ctx, player)

        print(f"Game ended after {self.ctx.turn + 1} turns")

        scores = [player.compute_score() for player in self.ctx.player_order]
        idx = np.argmax(scores)
        winner_name = self.ctx.player_order[idx].name
        winner_score = scores[idx]
        print(f"{winner_name} won with a score of {winner_score} points!")

        return (idx, scores)
