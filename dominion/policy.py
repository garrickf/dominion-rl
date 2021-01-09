"""Policies describe the actions an agent, such as the ComputerPlayer, should
take in any given situation.

Some policies, such as the TrainablePolicy, can be configured to run in train
or test mode.
"""

# Python stdlib
import random
from abc import ABC, abstractmethod
from typing import Any, Callable

import numpy as np


class Policy(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_input(self, options, **kwargs):
        pass


class RandomPolicy(Policy):
    def __init__(self) -> None:
        super().__init__()

    def get_input(self, options, allow_skip=True):
        if allow_skip:
            options = {**options, -1: "Skip"}

        chosen_action, label = random.choice(list(options.items()))
        if chosen_action == -1:
            return label  # "Skip"
        return chosen_action


class TrainablePolicy(Policy):
    def __init__(self, model, train=True) -> None:
        super().__init__()
        self.train = train
        self.model = model


class QLearningPolicy(TrainablePolicy):
    def __init__(
        self, model, raw_state_cb: Callable[..., Any], train=True, epsilon=0.3
    ) -> None:
        super().__init__(train=train, model=model)
        self.epsilon = epsilon
        self.prev_reward = None
        self.raw_state_cb = raw_state_cb

    def _get_raw_state(self):
        return self.raw_state_cb()

    def _extract_features(self, action: int, action_label: str):
        raw_state = self._get_raw_state()
        pass

    def _add_experience(self, reward: float, beta):
        pass

    def _get_best_action(self, options):
        # Get betas to feed to network by extracting features
        betas = [
            self._extract_features(action, label) for action, label in options.items()
        ]
        betas = np.array(betas)
        Q_vals = self.model.predict(betas)

        action_space = list(options.values())
        best_action = action_space[np.argmax(Q_vals)]
        best_action_beta = betas[np.argmax(Q_vals)]
        return best_action, best_action_beta

    def get_input(self, options, allow_skip=True):
        # If action allows skipping, add -1 to the options for actions. This
        # will become 0 in action space
        if allow_skip:
            options = {**options, -1: "Skip"}

        if self.train:
            """
            Uses a Epsilon-greedy policy that updates with each game (after model
            is trained)
            """
            if random.random() < self.epsilon:  # With probability epsilon, explore
                chosen_action, label = random.choice(list(options.items()))
                beta = self._extract_features(chosen_action, label)
            else:
                chosen_action, beta = self._get_best_action(options)

            # TODO: double check this
            if self.prev_reward is not None:
                reward = self.prev_reward
            else:
                reward = 0

            self._add_experience(reward, beta)
            return chosen_action
        else:
            chosen_action, beta = self._get_best_action(options)
            return chosen_action
