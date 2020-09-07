""" Controllers are hooked up to human players TODO: docstring
"""

import numpy as np
from input_util import get_line


def levenshtein_dist(w1, w2):
    """ Computes the Levenshtein distance between two strings.

    @param w1 (String): The first string
    @param w2 (String): The second string
    @return (int): The Levenstein distance between w1 and w2
    """
    # The indices i and j are one-indexed
    dist_matrix = np.zeros((len(w1) + 1, len(w2) + 1))

    for i in range(len(w1) + 1):
        for j in range(len(w2) + 1):
            if min(i, j) == 0:
                dist_matrix[i, j] = max(i, j)
            else:
                chars_equal = w1[i - 1] != w2[j - 1]
                dist_matrix[i, j] = min(
                    dist_matrix[i - 1, j] + 1,  # Deletion
                    dist_matrix[i, j - 1] + 1,  # Insertion
                    dist_matrix[i - 1, j - 1] + (1 if chars_equal else 0))

    return dist_matrix[-1, -1]


def fuzzy_text_match(text, options):
    """ Returns the index of the option that most closely matches the input
    text, along with the minimum edit distance.

    """
    # Format options and text
    text = text.lower()
    options = [s.lower() for s in options]
    dists = [levenshtein_dist(text, s) for s in options]
    best_idx = dists.index(min(dists))
    return best_idx, dists[best_idx]


def validator_from_options(options):
    """ Creates validator that take in Input object, cleans, and validates it.
    See input_util.py for more on how the validator object is used.
    """
    def is_valid_func(user_input):
        """ Checks to see if the input fuzzy matches one of the options, or 
        indexes one of the options. Turns the raw input into an int in the
        process.
        """
        if user_input.raw.isdigit():
            n = user_input.clean = int(user_input.raw)
            if n >= 0 and n < len(options):
                user_input.valid = True
                return
            else:
                user_input.err = 'Number out of range, try again.'
                return
        else:
            # Try fuzzy matching the string
            best_idx, edit_dist = fuzzy_text_match(user_input.raw, options)

            if edit_dist == 0:
                user_input.clean = best_idx
                user_input.valid = True
                return
            elif edit_dist <= 2:
                user_input.err = 'Did you mean "{}"?'.format(options[best_idx])
                return
            else:
                user_input.err = 'Invalid input, try again.'
                return

    return is_valid_func


class Controller:
    def __init__(self):
        pass

    def get_input(self, prompt, options, allow_skip=False):
        """ Prompts user for input and returns it as an integer choice from the 
        list options. Allows user to type strings or integers.
        """
        if allow_skip:
            options.append('Skip')

        c = get_line(prompt, validator=validator_from_options(options))
        return c
