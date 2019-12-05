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
    def __init__(self, featureExtractor, discount=0.95):
        self.weights = defaultdict(float)
        self.FILENAME = "WEIGHTS"
        self.featureExtractor = featureExtractor
        self.discount = discount
        self.numIters = 0
        
        # If pickle exists, load it in.
        try:
            infile = open(self.FILENAME, "rb")
            (weights, iters) = defaultdict(float, pickle.load(infile))
            self.weights, self.numIters = weights, iters
            infile.close()
        except IOError:
            print("No old weights to load in.")
            
    #TODO: IMPLEMENT QLEARNING OR SARSA
    #TODO: HANDLE TERMINAL STATE SOMEHOW
    def updateWeights(self, state, action, reward, newState):
        # check if 'state' is terminal, if so, no q-update
        estimate = self.getQ(state, action)
        # observation = 
        # 𝑄(𝑠,𝑎)←𝑄(𝑠,𝑎)+𝛼[𝑟+𝛾𝑄(𝑠′,𝑎′)−𝑄(𝑠,𝑎)]
        # θ ← θ + α(rt +γmaxθ⊤β(st+1,a)−θ⊤β(st,at))β(st,at)

    def getQ(self, state, action):
        # return 0 if state is terminal
        feature_vec = self.featureExtractor(state, action)
        return sparseDot(feature_vec, self.weights)


    def saveWeights(self):
        outfile = open(self.FILENAME,'wb')
        pickle.dump((dict(self.weights), self.numIters), outfile)
        outfile.close()


    def get_next_action(self, action_space, raw_state):
        return random.choice(action_space)

# qlp = QLearningPolicy()
# print(qlp.weights)
# qlp.weights = {"Hello":49}
# qlp.saveWeights()
# qlp2 = QLearningPolicy()
# print(qlp2.weights)