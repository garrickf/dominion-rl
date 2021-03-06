import numpy as np
from player import Player
from computer_player import ComputerPlayer
from table import Table
from card import AGENT_TYPES, PHASE_TYPES
from util import color_box
from utilities.log import Log
from utilities.console import Console
from policy import QLearningPolicy
import sys

NUM_PLAYERS = 2
game_log = Log()

class Dominion:
    def __init__(self, with_players=[], silence_output=False):
        class GameInformation():
            def __init__(self):
                """
                Inner class encapsulates the game information and exposes those
                properties to Player objects. Allows Players to get shared state
                information about the game.
                """
                self.table = Table(NUM_PLAYERS)
                self.players = []
                self.winning_player_number = None
                self.over = False
                self.margin = None
                self.rounds = None

        self.game_info = GameInformation()
        self.table = self.game_info.table # Convenience

        if with_players:
            for player in with_players:
                player.game_info = self.game_info # Add game information
            self.players = with_players
        else:
            # Create a game instance with two players
            # self.players = [Player(i+1) for i in range(NUM_PLAYERS)] # Two humans
            self.players = [
                Player(1, self.game_info), 
                ComputerPlayer(2, self.game_info)
            ] # One human, one computer

        self.game_info.players = self.players

        self.whose_turn = 0
        self.turns = 0
        self.rounds = 0

        # Clear game log (useful for repeated game instantiations)
        game_log.clear()

        if silence_output:
            game_log.set_verbose(False)
            Console.set_verbose(False)


    def play(self):
        """
        Play one game of Dominion. Cycle through all players, and for each player,
        run four phases (action, buy, cleanup, draw). The game could end after
        the action phase (i.e. if a card is obtained) or the buy phase, so the 
        state of the table is checked after both phases.

        Returns the index of the player who won, and the scores array
        """
        game_log.add_message('Starting game of Dominion...')
        while True:
            player = self.players[self.whose_turn]
            Console.clear()
            Console.log(color_box('{}\'s turn!'.format(player.raw_name), idx=player.player_number))
            game_log.add_message('{}\'s turn!'.format(player.name), suppress_output=True)

            # Action phase
            player.display_state()
            self_cache, other_cache = player.action_phase()
            if self.table.reached_end():
                break

            for action in other_cache:
                # Apply each action to every other player
                for other in [p for p in self.players if p != player]:
                    Console.clear()
                    Console.log(color_box('{} is attacked!'.format(other.raw_name), idx=other.player_number))
                    other.execute_action(action, PHASE_TYPES.IMMEDIATE, self_initiated=False)
            if self.table.reached_end():
                break

            # Reverting to player if an action affecting other players was played
            if other_cache:
                Console.clear()
                Console.log(color_box('{} resumes their turn...'.format(player.raw_name), idx=player.player_number))
                player.display_state()
                player.display_hand()
            
            # Buy phase
            for action in self_cache:
                player.execute_action(action, PHASE_TYPES.BUY, self_initiated=True)
            player.buy_phase()
            if self.table.reached_end():
                break

            # Cleanup phase
            player.cleanup_hand()
            # Draw phase
            player.draw_cards()

            self.turns += 1
            if self.turns % len(self.players) == 0:
                self.rounds += 1
            self.whose_turn = self.turns % len(self.players)

            if self.rounds == 250:
                print('Game timeout...')
                self.game_info.over = True
                self.game_info.margin = 100
                self.game_info.rounds = self.rounds

                for player in self.players:
                    player.reflect() # End of game reflection/terminal state

                return (1, [0, 0])

        scores = [player.compute_score() for player in self.players]
        idx = np.argmax(scores)
        margin = abs(scores[1] - scores[0]) # NOTE: assumes 2-player game
        game_log.add_message('{} won with a score of {}'.format(self.players[idx].name, scores[idx]))
        
        self.game_info.over = True
        self.game_info.winning_player_number = idx + 1
        self.game_info.margin = margin
        self.game_info.rounds = self.rounds

        for player in self.players:
            player.reflect() # End of game reflection/terminal state

        return (idx, scores)


    # Reset game instance in order to play again.
    def reset(self):
        self.players = [Player(i+1) for i in range(NUM_PLAYERS)]
        self.whose_turn = 0
        self.turns = 0
        self.rounds = 0
        self.table = Table(NUM_PLAYERS) # Should update in GameInfo struct too, right?


    def get_log(self):
        """
        Retrieves the game logs.
        """
        return game_log.full


def main():
    # Testing code (play a game!)
    filename = sys.argv[1] # Get weights

    policy = QLearningPolicy(from_weights=filename)
    players = [ComputerPlayer(1, policy=policy), Player(2)]
    dominion = Dominion(with_players=players)
    dominion.play()


if __name__ == '__main__':
    main()
