""" Game object TODO: docstring
"""

from dominion.common import *
import dominion.events as events
from dominion.players import HumanPlayer, ComputerPlayer
from .table import Table

# Game context stores order for players


class GameContext:
    def __init__(self, player_names):
        self.player_order = player_names
        self.event_queue = []
        self.table = Table(n_players=len(player_names))
        # On GameContext creation, scramble player order and create setup events

        for player_name in self.player_order:
            self.add_event(events.SetupEvent(target=player_name))

    def add_event(self, event, where=QueuePosition.BACK):
        """ Adds a list of events to the queue...
        """
        if where == QueuePosition.BACK:
            self.event_queue.append(event)
        elif where == QueuePosition.FRONT:
            self.event_queue.insert(0, event)

    def add_events(self, events, where=QueuePosition.BACK):
        """ Adds a list of events to the queue...
        """
        if where == QueuePosition.BACK:
            self.event_queue = self.event_queue + events
        elif where == QueuePosition.FRONT:
            self.event_queue = events + self.event_queue

    def get_next_event(self):
        # Create new turns if event queue empty
        if not self.event_queue:
            for player_name in self.player_order:
                self.add_event(events.PlayActionEvent(target=player_name))
                self.add_event(events.BuyEvent(target=player_name))
                self.add_event(events.CleanupEvent(target=player_name))

        return self.event_queue.pop(0)

    def reached_end(self):
        return False


class Game:
    """ Game objects manage a GameContext and multiple Controllers.
    """
    def __init__(self):
        # Initialize players
        players = []
        player_types = [PlayerType.HUMAN, PlayerType.HUMAN]
        for idx, player_type in enumerate(player_types):
            if player_type == PlayerType.HUMAN:
                player_name = 'player{}'.format(idx)
                player = HumanPlayer(player_name)
            if player_type == PlayerType.COMPUTER:
                player_name = 'player{} (CPU)'.format(idx)
                player = ComputerPlayer(player_name)
            players.append(player)

        self.name_to_player = {player.name: player for player in players}

        # Create GameContext
        self.ctx = GameContext(
            player_names=[player.name for player in players])

    def play(self):
        # While game not finished
        # Get next event from queue
        # Run event forward with game context, relevant player
        while not self.ctx.reached_end():
            event = self.ctx.get_next_event()
            # Get player and controller
            player = self.name_to_player[event.target]
            event.forward(self.ctx, player)
