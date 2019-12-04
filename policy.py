"""
A policy must implement:

get_next_action(action_space, current_state)
"""
import random

class Policy:
    def get_next_action(self, action_space, current_state):
        pass

class FixedPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        return action_space[0]

class RandomPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        return random.choice(action_space)

class QLearningPolicy(Policy):
    # Can play as it learns
    # Save weights after each game (pickle)
    
    def get_next_action(self, action_space, raw_state):
        return random.choice(action_space)