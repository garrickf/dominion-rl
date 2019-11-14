import numpy as np
from player import Player
from table import Table

NUM_PLAYERS = 2

class Dominion:
    def __init__(self):
        # Create a game instance with two players
        self.players = [Player(i+1) for i in range(NUM_PLAYERS)]
        self.turn = 0
        self.table = Table()

        # TODO: handle computer instance (with a computer class? computer controls player?)

    def play(self):
        # Play the game! While win condition not met, players take turns
        print('Starting game of Dominion...')
        while True:
            player = self.players[self.turn]
            print('Player {}\'s turn!'.format(self.turn+1))

            # Action phase
            player.display_hand()
            player.action_phase()
            # Buy phase, changes table
            # TODO: display status somehow?
            player.buy_phase(self.table)
            if self.table.reached_end():
                break

            # Cleanup phase
            player.cleanup_hand()
            # Draw phase
            player.draw_cards()
            player.display_hand()

            self.turn = (self.turn + 1) % len(self.players)

        scores = [player.compute_score() for player in self.players]
        idx = np.argmax(scores)
        print('Player {} won with a score of {}'.format(idx+1, scores[idx]))

    # TODO: reset game instance in order to play again.
    def reset(self):
        self.players = [Player(i+1) for i in range(NUM_PLAYERS)]
        self.turn = 0
        self.table = Table()

dominion = Dominion()
dominion.play()