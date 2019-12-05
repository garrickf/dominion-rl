"""
A policy must implement:

- get_next_action(action_space, current_state)
- a train flag to alter actions that are chosen in get_next_action. This is 
  useful if we are training and need to explore randomly, versus maximizing
  reward.
"""
import numpy as np
import random
import pickle
from collections import defaultdict
from util import sparseDot

class Policy:
    def __init__(self):
        self.train = True


    def get_next_action(self, action_space, current_state):
        pass


    def set_train(self, is_training):
        self.train = is_training


class FixedPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        return action_space[0]


class RandomPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        return random.choice(action_space)


class HardCodedPolicy(Policy):
    def get_next_action(self, action_space, current_state):
        pass # TODO: make a hard coded policy


class QLearningPolicy(Policy):
    # Can play as it learns
    # Save weights after each game (pickle)
    # Can only update weights of PREVIOUS thing AFTER this phase
    #Computer extracts raw state, we extract FEATURES here.
    def __init__(self, discount=0.95):
        super().__init__() # Call parent constructor
        self.weights = defaultdict(float)
        self.FILENAME = "WEIGHTS"
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

        # TODO: Need to keep track of old state (s), action (a) and old reward (r), 
        # so newly observed state (sp) can be used in update
    

    def extract_features(raw_state, action): # TODO: include action name
        """
        When given the raw state by the computer player, extract relevant features
        and return a one-dimensional vector with n components, where n is the number
        of features. This will be provided as input to the QLearning algorithm.
        """

        # Unpack entries from raw_state
        table = raw_state['table']
        players = raw_state['players']
        # TODO: add whose turn, number of rounds so far, current player's deck n hand...

        # TODO: dbl-check and revise code below...

        ###### Features about the player. ######
        hand, draw_pile, discard_pile = (player.hand, 
            player.deck.draw_pile, player.deck.discard_pile)
        
        # Variable for number of each card in hand
        money = 0
        for card in hand:
            key = (card.name, "N in Hand")
            state[key] += 1
            if card.type == CARD_TYPES.TREASURE:
                money += card.treasure_value
        
        # Variable for total money in hand
        state["Total Money In Hand"] = money

        # Variable for card in each position in hand
        for i in range(len(hand)):
            key = ("Card at index", i, hand[i].name)

        ###### Features about the supply. ######
        kingdom = table.kingdom
        
        # Indicator variables for the cards in the kingdom
        for card in kingdom:
            key = (card.name, "In Kingdom?")
            state[key] = 1

        # Variable for number of each card in the supply
        for card in table.keys():
            key = (card.name, "N in Supply")
            state[key] = table.get(card)

        ###### Features about other players. ######

        # Variable for total VP in deck of each player       
    
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
        """
        If in training mode, get_next_action follows a certain policy. Otherwise,
        it plays hard with the weights it has learned over time.
        """
        if self.train:
            return random.choice(action_space)
        else:
            #TODO: use theta and extract features to choose action. Sketched below:
            features = [extract_features(raw_state, action) for action in action_space]
            Q_vals = [sparseDot(f, self.weights) for f in features]
            best_action = action_space[np.argmax(Q_vals)]
            return best_action

# qlp = QLearningPolicy()
# print(qlp.weights)
# qlp.weights = {"Hello":49}
# qlp.saveWeights()
# qlp2 = QLearningPolicy()
# print(qlp2.weights)