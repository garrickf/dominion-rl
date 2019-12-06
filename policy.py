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
from model import Model

np.random.seed(1)
random.seed(1)

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
    def __init__(self, discount=0.95, instanced=False):
        super().__init__() # Call parent constructor
        
        self.weights = np.zeros((440, )) # TODO: remove
        self.discount = discount
        # TODO: add epsilon exploration, etc.
        
        # TODO: fix file loading, add a provided kwarg for the source file
        # If pickle exists, load it in.
        # try:
        #     infile = open(self.FILENAME, "rb")
        #     (weights, iters) = defaultdict(float, pickle.load(infile))
        #     self.weights, self.numIters = weights, iters
        #     infile.close()
        # except IOError:
        #     print("No old weights to load in.")
        
        if instanced:
            self.model = Model.get_model_instance()
        else:
            self.model = Model.get_model()
        
        # self.model.summary() # Debug

        self.experiences = []
        self.prev_beta = []
        self.prev_r = None


    def extract_features(self, raw_state, action): # TODO: include action name
        """
        When given the raw state by the computer player, extract relevant features
        and return a one-dimensional vector with n components, where n is the number
        of features. This will be provided as input to the QLearning algorithm.
        """
        # TODO: clean up
        EYE = np.eye(100) # Only 100 sparse vectors can be pulled!

        # Unpack entries from raw_state
        table = raw_state['table']
        players = raw_state['players']
        me = players[0] # TODO: fix this later, player 0 may not always be us!
        
        # TODO: add whose turn, number of rounds so far, current player's deck n hand...

        all_features = np.array([])

        """
        Features about action being taken

        One hot vector of the action is produced. Think of it like visual input:
        we type the number specified by the one-hot.
        """
        # Shift all actions by one
        if action == None: 
            action = 0
        else:
            action += 1
        action_one_hot = EYE[action]
        all_features = np.concatenate([all_features, action_one_hot])

        """
        Features about ourselves

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

        all_features = np.concatenate([all_features, targets.flatten()])

        assert(all_features.shape[0] == 440)
        assert(not np.isnan(np.sum(all_features)))
        
        """
        Features about the table

        Store this as a vector the size of the number of distinct cards. Store
        the number of cards remaining in each component of the vector.
        """
        present = []
        for card in table.cards:
            left = table.table[card]
            idx = get_card_id(card)
            present.append(np.eye(NUM_CARDS)[idx] * left)

        present = np.sum(present, axis=0)
        all_features = np.concatenate([all_features, present])

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
    
    def update_weights_old(self, new_beta, new_r):
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

        # if new_r > 0:
        #     print('got new reward > 0')
        # if r_cached > 0:
        #     print('taking out cached reward > 0')
        
        # Q_hat = self.weights.T.dot(beta_cached)
        # Qp_hat = self.weights.T.dot(new_beta) # IDEA: Qp_hat should be 0 at the end

        Q_hat = self.model.predict(beta_cached.reshape(1, -1))
        Qp_hat = self.model.predict(new_beta.reshape(1, -1))

        # print('Q vals, predicted', Q_hat, Qp_hat)

        # Compute delta (no need for temporal difference)
        # delta = r_cached + self.discount * Qp_hat - Q_hat
        
        # Update theta
        # TODO: bug with mult by beta
        # old_weights = self.weights
        # self.weights += self.learning_rate * delta * beta_cached # Add to numpy array
        """
        NN aproach (no TD)
        """
        y = r_cached + self.discount * Qp_hat
        print('Ideal y', y)
        self.model.train_on_batch(beta_cached.reshape(1, -1), y)

        if(np.max(self.weights) > 100):
            print('Higher Qval than end state reward')
            print('Qhat', Q_hat, 'old weights', old_weights, 'beta_cached', beta_cached)
            assert(False)

        if np.isnan(np.sum(self.weights)):
            print('It got bad')
            print('Qhat', Q_hat, 'old weights', old_weights, 'beta_cached', beta_cached)

            assert(False)
        # THOUGHT: is weighing by beta okay with indicator features (these aren't scaled, they are binary!)

        # Cache most recent beta and r
        self.beta = new_beta
        self.r = new_r


    def getQ(self, state, action):
        # TODO: remove, perhaps
        # return 0 if state is terminal
        feature_vec = self.featureExtractor(state, action)
        return sparseDot(feature_vec, self.weights)


    def get_weights(self):
        # TODO: fix
        return self.weights


    def update_weights(self):
        """
        NN Draft: update weights with self.experience

        New: with reward (triggered by reflection on previous experience), decay
        reward backwards through past actions (if I won, these actions were good)
        """
        if not self.train: return # Do not update model in test mode

        betas, rewards = zip(*self.experiences) # Unzip

        # Propagate final reward back through list of rewards 
        betas = np.array(betas)
        rewards = np.array(rewards, dtype=np.float64)
        decay = [0.99 ** (len(rewards) - i - 1) for i in range(len(rewards))] # 0.99 seems good
        decay[-1] = 0 # Decay does not apply to last reward
        last_reward = rewards[-1]
        
        rewards += last_reward * np.array(decay)
        
        print('Learing on {} experience tuples.'.format(len(betas)))
        # print(rewards)

        old_beta = betas[0]
        old_reward = rewards[0]
        for i in range(1, len(rewards)):
            beta = betas[i]
            reward = rewards[i]
            
            Q_hat = self.model.predict(old_beta.reshape(1, -1))
            Qp_hat = self.model.predict(beta.reshape(1, -1))
            # print('Q vals, predicted', Q_hat, Qp_hat) # Debug

            # old   new
            # . . . x x x
            # s a r s a r
            y = old_reward + self.discount * Qp_hat
            # print('Ideal y', y) # Debug
            loss = self.model.train_on_batch(old_beta.reshape(1, -1), y)
            # print(loss, 'loss') # Loss is in the 9000's

            old_beta = beta
            old_reward = reward

            # TODO: will miss final reward? does it matter?

        # Refresh: once we've learned, discard experiences and start over
        self.experiences = []
        self.prev_beta = []
        self.prev_r = None


    def add_experience(self, beta, reward):
        """
        Called each time the policy is asked to return a new action. In training
        mode, the policy needs to cache the beta (an (s, a) encoding) and reward
        for later, to learn from the experience.
        """
        if not self.train: return # Do not collect experience in test mode

        if self.prev_r is None:
            self.prev_r = 0 # Begin recording rewards (value 0 is meaningless)
            self.prev_beta = beta
            return # Wait for next r to get a full exp tuple

        self.experiences.append((self.prev_beta, reward))
        self.prev_r = reward
        self.prev_beta = beta


    def get_next_action(self, action_space, raw_state, reward=0): # TODO: include phase (perhaps in GameInfo?)
        """
        If in training mode, get_next_action follows a certain policy. Otherwise,
        it plays (hard) with the weights it has learned over time.

        If enough information exists for an experience tuple, updates weights.
        """
        def get_best_action(action_space, raw_state):
            # Extract features, calculate betas, feed to network for processing.
            # print('calculating q vals for action space of size {}'.format(len(action_space)))
            betas = [self.extract_features(raw_state, action) for action in action_space]
            betas = np.array(betas)
            Q_vals = self.model.predict(betas)
            # print(Q_vals) # Debug
            best_action = action_space[np.argmax(Q_vals)]
            return best_action

        if self.train:
            """
            Uses a Epsilon-greedy policy that updates with each game (after model
            is trained)
            """
            if random.random() < 0.3: # With probability epsilon, explore
                chosen_action = random.choice(action_space)
            else:
                chosen_action = get_best_action(action_space, raw_state)
            beta = self.extract_features(raw_state, chosen_action)

            self.add_experience(beta, reward)
            return chosen_action
        else:
            return get_best_action(action_space, raw_state)


# qlp = QLearningPolicy()
# print(qlp.weights)
# qlp.weights = {"Hello":49}
# qlp.saveWeights()
# qlp2 = QLearningPolicy()
# print(qlp2.weights)