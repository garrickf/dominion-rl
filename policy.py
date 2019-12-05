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
from card import get_card_id, ALL_CARDS

NUM_CARDS = len(ALL_CARDS)

class Policy:
    def __init__(self):
        self.train = True


    def get_next_action(self, action_space, current_state, reward=None):
        pass


    def set_train(self, is_training):
        self.train = is_training


    def get_weights(self):
        return []


    def update_weights(self):
        pass


class FixedPolicy(Policy):
    def get_next_action(self, action_space, current_state, reward=None):
        return action_space[0]


class RandomPolicy(Policy):
    def get_next_action(self, action_space, current_state, reward=None):
        return random.choice(action_space)


class HardCodedPolicy(Policy):
    def get_next_action(self, action_space, current_state, reward=None):
        pass # TODO: make a hard coded policy


class QLearningPolicy(Policy):
    # Can play as it learns
    # Save weights after each game (pickle)
    # Can only update weights of PREVIOUS thing AFTER this phase
    # Computer extracts raw state, we extract FEATURES here.
    # NOTE: writing out files is a responsibility deferred to learn_dominion.py
    def __init__(self, discount=0.95):
        super().__init__() # Call parent constructor
        
        # self.weights = defaultdict(float)
        self.weights = np.zeros((340, ))
        self.discount = discount
        self.learning_rate = 0.9
        
        # TODO: fix file loading, add a provided kwarg for the source file
        # If pickle exists, load it in.
        # try:
        #     infile = open(self.FILENAME, "rb")
        #     (weights, iters) = defaultdict(float, pickle.load(infile))
        #     self.weights, self.numIters = weights, iters
        #     infile.close()
        # except IOError:
        #     print("No old weights to load in.")

        # TODO: Need to keep track of old state (s), action (a) and old reward (r), 
        # so newly observed state (sp) can be used in update

        self.beta = []
        self.r = None


    def extract_features(self, raw_state, action): # TODO: include action name
        """
        When given the raw state by the computer player, extract relevant features
        and return a one-dimensional vector with n components, where n is the number
        of features. This will be provided as input to the QLearning algorithm.
        """

        # Unpack entries from raw_state
        table = raw_state['table']
        players = raw_state['players']
        me = players[0] # TODO: fix this later, player 0 may not always be us!
        
        # TODO: add whose turn, number of rounds so far, current player's deck n hand...

        all_features = []

        """
        Features about ourself

        Note: get_card_id takes as input a card and returns an index associated
        with it. This consistency lets us refer to cards by number when constructing
        the feature vector.

        Hand: weird, because you can have almost unbounded number of cards in hand. How many one-hot
        vectors do we extract?
        """
        hand, draw_pile, discard_pile = (me.hand, me.deck.draw_pile, me.deck.discard_pile)
        idxs = []
        for card in hand:
            idxs.append(get_card_id(card))
        
        # Example code to create a bunch of one-hot vectors
        targets = np.eye(NUM_CARDS)[idxs] # Repeatedly sample rows of the id matrix
        if targets.shape[0] < 10:
            # Pad up to 10 cards with zeros for 'no card' (=340 params)
            pad = np.zeros((10 - targets.shape[0], targets.shape[1]))
            targets = np.concatenate([targets, pad], axis=0)

        assert(targets.shape[0] == 10 and targets.shape[1] == 34)

        all_features = targets.reshape(-1)
        return all_features # NOTE: right now, features are just: what's in hand

        # TODO: dbl-check, revise, and reincorporate code below...
        
        # # Variable for number of each card in hand
        # money = 0
        # for card in hand:
        #     key = (card.name, "N in Hand")
        #     state[key] += 1
        #     if card.type == CARD_TYPES.TREASURE:
        #         money += card.treasure_value
        
        # # Variable for total money in hand
        # state["Total Money In Hand"] = money

        # # Variable for card in each position in hand
        # for i in range(len(hand)):
        #     key = ("Card at index", i, hand[i].name)

        # ###### Features about the supply. ######
        # kingdom = table.kingdom
        
        # # Indicator variables for the cards in the kingdom
        # for card in kingdom:
        #     key = (card.name, "In Kingdom?")
        #     state[key] = 1

        # # Variable for number of each card in the supply
        # for card in table.keys():
        #     key = (card.name, "N in Supply")
        #     state[key] = table.get(card)

        # ###### Features about other players. ######

        # # Variable for total VP in deck of each player       
    
    #TODO: IMPLEMENT QLEARNING OR SARSA
    #TODO: HANDLE TERMINAL STATE SOMEHOW
    def update_weights(self, new_beta, new_r):
        # check if 'state' is terminal, if so, no q-update
        # estimate = self.getQ(state, action)
        # observation = 
        # 𝑄(𝑠,𝑎)←𝑄(𝑠,𝑎)+𝛼[𝑟+𝛾𝑄(𝑠′,𝑎′)−𝑄(𝑠,𝑎)]
        # θ ← θ + α(rt +γmaxθ⊤β(st+1,a)−θ⊤β(st,at))β(st,at)

        """
        Update weights using SARSA in a delayed fashion, as new experiences
        come in. This is because it takes multiple player turns to create one
        experience tuple, so previous turns have to be cached:
    
                                      another turn...
                                      ----------
                           one turn
                           ---------
        experience n:      s   a   r  sp  ap
        experience n + 1:  -----      s   a   r  sp  ap
                           beta       -----
                                      betap
        
        In each turn, we get s, a, and r. s and a are passed through extract_features
        to get the feature vector beta.
        """

        # NOTE: this is SARSA! TODO: impl. Q learning or fix...
        # Compute interpolated Q values
        if self.r is None:
            self.r = 0 # Start reward at 0
            self.beta = new_beta
            return # Wait for next r to get a full exp tuple

        # We have enough information to update weights with one experience tuple
        beta_cached = self.beta
        r_cached = self.r
        
        Q_hat = self.weights.T.dot(beta_cached)
        Qp_hat = self.weights.T.dot(new_beta)

        # Compute delta
        delta = r_cached + self.discount * Qp_hat - Q_hat
        
        # Update theta
        self.weights += self.learning_rate * delta #* new_beta # Add to numpy array
        # THOUGHT: is weighing by beta okay with indicator features (these aren't scaled, they are binary!)

        # Cache most recent beta and r
        self.beta = new_beta
        self.r = new_r


    def getQ(self, state, action):
        # return 0 if state is terminal
        feature_vec = self.featureExtractor(state, action)
        return sparseDot(feature_vec, self.weights)


    def get_weights(self):
        return self.weights


    def get_next_action(self, action_space, raw_state, reward=0): # TODO: include phase (perhaps in GameInfo?)
        """
        If in training mode, get_next_action follows a certain policy. Otherwise,
        it plays (hard) with the weights it has learned over time.

        If enough information exists for an experience tuple, updates weights.
        """
        if self.train:
            chosen_action = random.choice(action_space)
            beta = self.extract_features(raw_state, chosen_action)
            
            # Update weights
            self.update_weights(beta, reward)

        else:
            # TODO: use theta and extract features to choose action. Sketched below:
            # features = [self.extract_features(raw_state, action) for action in action_space]
            # Q_vals = [sparseDot(f, self.weights) for f in features]
            # best_action = action_space[np.argmax(Q_vals)]
            # return best_action
            return random.choice(action_space)


# qlp = QLearningPolicy()
# print(qlp.weights)
# qlp.weights = {"Hello":49}
# qlp.saveWeights()
# qlp2 = QLearningPolicy()
# print(qlp2.weights)