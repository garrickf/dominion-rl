"""
A computer player extends a (human) player with a fixed policy.
"""
from policy import FixedPolicy, RandomPolicy
from player import Player
from collections import defaultdict

class ComputerPlayer(Player):
    def __init__(self, i, game_info):
        super().__init__(i, game_info) # Call parent constructor
        self.type = 'Computer'
        self.policy = RandomPolicy()


    #TODO: add method to extract all state
    #TODO: figure out how to get table/other player info in here
    # Right now, cannot reason about other players, only game state (table) and self
    def extractFeatures():
        table = self.game.table
        players = self.game.players
        state = defaultdict(float)
        
        return state

    #TODO: fix execute action, action_phase, buy_phase by replacing choose
    def choose(self, choice_set, **kwargs):
        return self.policy.get_next_action(choice_set, None) #TODO: extract current state
