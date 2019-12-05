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
        reward = self.get_reward()
        raw_state = self.extract_raw_state()
        self.policy.get_next_action([None], raw_state, reward=reward) # Only one action: we won
        # print(self.policy.get_weights())


    # TODO: make a player function that experiences reward, and feed that to the computer player
    def get_reward(self):
        reward = 0
        if self.game.over and self.player_number == self.game.winning_player_number:
            reward = 100
        
        # TODO: other heuristic rewards can be added here

        return reward
