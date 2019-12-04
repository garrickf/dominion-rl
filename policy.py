"""
A policy must implement:

get_next_action(action_space, current_state)
"""
import random
import pickle
from collections import defaultdict
from util import sparseDot

class Policy:
    def get_next_action(self, action_space, current_state):
        pass

class FixedPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        return action_space[0]

class RandomPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        return random.choice(action_space)

class HardCodedPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        pass

class QLearningPolicy(Policy):
    # Can play as it learns
    # Save weights after each game (pickle)
    def __init__(self, featureExtractor):
        self.weights = defaultdict(float)
        self.FILENAME = "WEIGHTS"
        self.featureExtractor = featureExtractor
        
        # If pickle exists, load it in.
        try:
            infile = open(self.FILENAME, "rb")
            self.weights = defaultdict(float, pickle.load(infile))
            infile.close()
        except IOError:
            print("No old weights to load in.")
            
    #TODO: IMPLEMENT QLEARNING OR SARSA
    #TODO: HANDLE TERMINAL STATE SOMEHOW
    def updateWeights(self):
        pass

    def getQ(self, state, action):
        feature_vec = self.featureExtractor(state, action)
        return sparseDot(feature_vec, self.weights)


    def saveWeights(self):
        outfile = open(self.FILENAME,'wb')
        pickle.dump(dict(self.weights), outfile)
        outfile.close()


    def get_next_action(self, action_space, raw_state):
        return random.choice(action_space)

qlp = QLearningPolicy()
print(qlp.weights)
qlp.weights = {"Hello":49}
qlp.saveWeights()
qlp2 = QLearningPolicy()
print(qlp2.weights)