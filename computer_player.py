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
        raw_state = self.extract_raw_state()
        return self.policy.get_next_action(choice_set, raw_state)
