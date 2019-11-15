import numpy as np
import os
from player import Player
from table import Table
from card import AGENT_TYPES, PHASE_TYPES
from util import color_box

NUM_PLAYERS = 2

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
        print('Starting game of Dominion...')
        while True:
            player = self.players[self.turn]
            os.system('clear')
            print(color_box('Player {}\'s turn!'.format(self.turn+1), idx=self.turn+1))
                                          
            # Action phase
            player.display_state()
            action_cache = player.action_phase(self.table)
            if self.table.reached_end():
                break

            for action in action_cache:
                # Apply each action to every other player
                for other in [p for p in self.players if p != player]:
                    other.execute_action(action, PHASE_TYPES.IMMEDIATE, self.table, self_initiated=False)
            if self.table.reached_end():
                break
            
            # Buy phase
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
        print('Player {} won with a score of {}'.format(idx+1, scores[idx]))


    # TODO: reset game instance in order to play again.
    def reset(self):
        self.players = [Player(i+1) for i in range(NUM_PLAYERS)]
        self.turn = 0
        self.table = Table(NUM_PLAYERS)

dominion = Dominion()
dominion.play()