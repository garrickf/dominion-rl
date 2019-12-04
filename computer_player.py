"""
A computer player extends a (human) player with a fixed policy.
"""
from policy import FixedPolicy, RandomPolicy
from player import Player

class ComputerPlayer(Player):
    def __init__(self, i):
        super().__init__(i) # Call parent constructor
        self.type = 'Computer'
        self.policy = RandomPolicy()


    #TODO: add method to extract all state

    #TODO: add way for player object to query game for external objects (Table, other Players, etc.)

    #TODO: fix execute action, action_phase, buy_phase by replacing choose
    def choose(self, choice_set, **kwargs):
        return self.policy.get_next_action(choice_set, None) #TODO: extract current state
