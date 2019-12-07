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

from utilities.filelog import FileLog

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


    def add_last_experience(self, reward):
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
    def __init__(self, discount=0.95, instanced=False, fileid=1, from_weights=None):
        super().__init__() # Call parent constructor

        self.discount = discount
        self.decay = 0.9

        self.num_features = 644 # TODO: update as more features added

        # TODO: add epsilon exploration, etc.
        
        if instanced:
            self.model = Model.get_model_instance()
        else:
            self.model = Model.get_model()

        if from_weights is not None:
            self.model.load_weights(from_weights)
        
        # self.model.summary() # Debug

        self.experiences = []
        self.prev_beta = None

        self.file = FileLog.file('pol{}-losses'.format(fileid))


    def get_sentinel(self):
        """
        The sentinel beta (s, a) encoding is just a vector of zeros, fed to the 
        network. Hopefully, the network doesn't assign Q-value to the sentinel-
        otherwise, it may inflate prior estimates of Q-value and explode...
        """
        return np.zeros((self.num_features,))


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
        if targets.shape[0] < 15:
            # Pad up to 15 cards with zeros for 'no card' (=340 params)
            pad = np.zeros((15 - targets.shape[0], targets.shape[1]))
            targets = np.concatenate([targets, pad], axis=0)
        all_features = np.concatenate([all_features, targets.flatten()])
        
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
        
        # print(all_features.shape[0])
        assert(all_features.shape[0] == self.num_features)
        return all_features

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


    def save_weights(self, filepath):
        self.model.save_weights(filepath)


    def update_weights(self):
        """
        NN Draft: update weights with self.experience

        New: with reward (triggered by reflection on previous experience), decay
        reward backwards through past actions (if I won, these actions were good)
        """
        if not self.train: return # Do not update model in test mode

        betas, rewards = zip(*self.experiences) # Unzip

        # print(rewards)

        # Propagate final reward back through list of rewards 
        betas = np.array(betas)
        rewards = np.array(rewards, dtype=np.float64)
        decay = [self.decay ** (len(rewards) - i - 1) for i in range(len(rewards))] # 0.9 seems good
        decay[-1] = 0 # Decay does not apply to last reward
        last_reward = rewards[-1]
        
        rewards += last_reward * np.array(decay)
        print('(policy) Learning on {} experience tuples.'.format(len(betas)))
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
            self.file.write(loss)
            # print('(policy) loss: {}'.format(loss)) # Loss is in the 9000's

            old_beta = beta
            old_reward = reward

            # TODO: will miss final reward? does it matter?

        # Refresh: once we've learned, discard experiences and start over
        self.experiences = []
        self.prev_beta = None


    def add_experience(self, reward, beta):
        """
        Called each time the policy is asked to return a new action. In training
        mode, the policy needs to cache the beta (an (s, a) encoding) and reward
        for later, to learn from the experience.
        """
        if not self.train: return # Do not collect experience in test mode

        if self.prev_beta is None:
            self.prev_beta = beta
            return # Wait for next time to get a full exp tuple

        self.experiences.append((self.prev_beta, reward))
        self.prev_beta = beta


    def add_last_experience(self, reward):
        beta = self.get_sentinel() # The last beta is a cap
        self.add_experience(reward, beta)


    def get_next_action(self, action_space, raw_state, reward=0):
        """
        If in training mode, get_next_action follows a certain policy. Otherwise,
        it plays (hard) with the weights it has learned over time. Receives
        r, s (previous reward!) from the game.

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
            best_action_beta = betas[np.argmax(Q_vals)]
            return best_action, best_action_beta

        if self.train:
            """
            Uses a Epsilon-greedy policy that updates with each game (after model
            is trained)
            """
            if random.random() < 0.3: # With probability epsilon, explore
                chosen_action = random.choice(action_space)
                beta = self.extract_features(raw_state, chosen_action)
            else:
                chosen_action, beta = get_best_action(action_space, raw_state)

            self.add_experience(reward, beta)
            return chosen_action
        else:
            chosen_action, beta = get_best_action(action_space, raw_state)
            return chosen_action


# qlp = QLearningPolicy()
# print(qlp.weights)
# qlp.weights = {"Hello":49}
# qlp.saveWeights()
# qlp2 = QLearningPolicy()
# print(qlp2.weights)