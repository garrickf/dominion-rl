"""
A computer player extends a (human) player with a fixed policy.
"""
from policy import FixedPolicy, RandomPolicy
from player import Player

class ComputerPlayer(Player):
    def __init__(self, i, game_info={}, policy=RandomPolicy()):
        super().__init__(i, game_info) # Call parent constructor
        self.type = 'Computer'
        self.policy = policy


    def extract_raw_state(self):
        table = self.game.table
        players = self.game.players

        state = {
            'table': table,
            'players': players,
            # TODO: add more information as needed...
        }
        
        return state


    def choose(self, choice_set, **kwargs): # TODO: choose needs kwargs fleshed out
        reward = self.get_reward()
        raw_state = self.extract_raw_state()
        return self.policy.get_next_action(choice_set, raw_state, reward=reward)


    def reflect(self):
        """
        Method which updates the policy installed given recent experiences. 
        Policies (and their associated models) are responsible for collecting
        experiences and training themselves with the command update_weights.
        """
        reward = self.get_reward()
        raw_state = self.extract_raw_state()
        self.policy.get_next_action([None], raw_state, reward=reward) # Actions don't matter: we won

        self.policy.update_weights() # Reflect on game experience


    def get_reward(self):
        """
        Helper function to assign reward given game state. Most reward is sparse:
        it is assigned at the end of the game. The player receives the most reward
        for simply winning; an addition bonus is given for the margin by which the
        player wins; this hopefully incentivizes trouncing, but not too much that
        it becomes hubris.
        """
        reward = 0
        if self.game.over:
            if self.player_number == self.game.winning_player_number:
                reward = 100 + self.game.margin * 10
                print('Player {} won, reward of {}'.format(self.player_number, reward))
            else:
                reward = -100 - self.game.margin * 10
        
        # TODO: other heuristic rewards can be added here

        return reward
