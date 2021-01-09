"""Functions dealing with getting input from human players.
"""

import sys
from colorama import Fore, Back, Style

REMOVE_LINE_CODE = '\033[F'
CLEAR_TO_END_CODE = '\033[K'

opening_prompt = lambda s: '[{}{}{}]'.format(Fore.YELLOW, s, Style.RESET_ALL)
with_warning_style = lambda s: '{}{}{}'.format(Fore.RED, s, Style.RESET_ALL)


def remove_lines(n=2):
    """ Clears and removes lines from the console.
    """
    for i in range(n):
        sys.stdout.write(CLEAR_TO_END_CODE)
        sys.stdout.write(REMOVE_LINE_CODE)


# Hold raw input and cleaned output (just an integer)
class Input:
    """ Holds raw and clean input, as well as whether the input is valid or not.
    """
    def __init__(self, prompt):
        self.raw = input(prompt)
        self.valid = False
        self.clean = None
        self.err = None


def get_line(prompt_str, validator=None):
    """ Gets input from user, with optional formatter/validator to act on input
    for formatting and validation purposes.
    """
    print('{} {}'.format(opening_prompt('?'), prompt_str))
    while True:
        user_input = Input('> ')
        if not validator:
            return user_input.raw

        validator(user_input)
        if user_input.valid:
            return user_input.clean

        remove_lines()
        print('{} {}'.format(opening_prompt('?'), prompt_str),
              with_warning_style(user_input.err))
