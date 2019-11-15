import numpy as np
import os
from player import Player
from table import Table
from card import AGENT_TYPES, PHASE_TYPES
from util import color_box
from utilities.log import Log

NUM_PLAYERS = 2
game_log = Log()

class Dominion:
    def __init__(self):
        # Create a game instance with two players
        self.players = [Player(i+1) for i in range(NUM_PLAYERS)]
        self.turn = 0
        self.table = Table(NUM_PLAYERS)
        # TODO: handle computer instance (with a computer class? computer controls player?)


    def play(self):
        """
        Play one game of Dominion. Cycle through all players, and for each player,
        run four phases (action, buy, cleanup, draw). The game could end after
        the action phase (i.e. if a card is obtained) or the buy phase, so the 
        state of the table is checked after both phases.
        """
        game_log.add_message('Starting game of Dominion...')
        while True:
            player = self.players[self.turn]
            os.system('clear')
            print(color_box('{}\'s turn!'.format(player.raw_name), idx=player.player_number))
            game_log.add_message('{}\'s turn!'.format(player.name), suppress_output=True)

            # Action phase
            player.display_state()
            self_cache, other_cache = player.action_phase(self.table)
            if self.table.reached_end():
                break

            for action in other_cache:
                # Apply each action to every other player
                for other in [p for p in self.players if p != player]:
                    os.system('clear')
                    print(color_box('{} is attacked!'.format(other.name), idx=other.player_number))
                    other.execute_action(action, PHASE_TYPES.IMMEDIATE, self.table, self_initiated=False)
            if self.table.reached_end():
                break

            # Reverting to player if an action affecting other players was played
            if other_cache:
                os.system('clear')
                print(color_box('{} resumes their turn...'.format(player.name), idx=player.player_number))
                player.display_state()
                player.display_hand()
            
            # Buy phase
            for action in self_cache:
                player.execute_action(action, PHASE_TYPES.BUY, self.table, self_initiated=True)
            player.buy_phase(self.table)
            if self.table.reached_end():
                break

            # Cleanup phase
            player.cleanup_hand()
            # Draw phase
            player.draw_cards()

            self.turn = (self.turn + 1) % len(self.players)

        scores = [player.compute_score() for player in self.players]
        idx = np.argmax(scores)
        game_log.add_message('Player {} won with a score of {}'.format(idx+1, scores[idx]))


    # TODO: reset game instance in order to play again.
    def reset(self):
        self.players = [Player(i+1) for i in range(NUM_PLAYERS)]
        self.turn = 0
        self.table = Table(NUM_PLAYERS)

dominion = Dominion()
dominion.play()