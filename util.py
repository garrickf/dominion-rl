import sys
from colorama import Fore, Back, Style
import re

def sparseDot(v, w):
    return sum(v[k] * w[k] for k in set(v.keys()) & set(w.keys()))


# 7-bit C1 ANSI sequences
ansi_escape = re.compile(r'''
    \x1B    # ESC
    [@-_]   # 7-bit C1 Fe
    [0-?]*  # Parameter bytes
    [ -/]*  # Intermediate bytes
    [@-~]   # Final byte
''', re.VERBOSE)
def strip_style(text):
    """
    Adapted from Stack Overflow: 
    https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    """
    return ansi_escape.sub('', text)


def get_integer(prompt):
    typed = input(prompt)
    if typed.isdigit():
        return int(typed)
    elif typed == '':
        return None


def get_integer_or_none(prompt, reprompt=None):
    """
    Prompt for a non-negative integer, or None. Accepts a reprompt if the input
    is invalid in the caller, and the caller would like to reprompt again.
    """
    if reprompt:
        # Reprompt is only used when a consuming function finds the input invalid.
        sys.stdout.write(REMOVE_LINE + REMOVE_LINE)
        sys.stdout.write(CLEAR_TO_END) # Clears line
        print('{} {} {}'.format(QMARK, prompt, invalid(reprompt)))
    else:
        print('{} {}'.format(QMARK, prompt))
    sys.stdout.write(CLEAR_TO_END) # Clears line
    typed = input('> ')
    
    while not typed.isdigit() and typed != '':
        sys.stdout.write(REMOVE_LINE + REMOVE_LINE)
        sys.stdout.write(CLEAR_TO_END) # Clears line
        print('{} {} {}'.format(QMARK, prompt, invalid('Invalid input, try again.')))
        sys.stdout.write(CLEAR_TO_END) # Clears line
        typed = input('> ')

    if typed.isdigit():
        return int(typed)
    elif typed == '':
        return None


def get_choice(prompt, choice_set=None):
    """
    Wrapper function that accepts a choice set and prompts for a valid choice in
    the choice set, or any non-negative integer/None otherwise.
    """
    choice = get_integer_or_none(prompt)
    while choice_set and choice not in choice_set:
        choice = get_integer_or_none(prompt, 'Invalid choice!')
    return choice


switcher = {
    0: Fore.WHITE,
    1: Fore.RED, 
    2: Fore.BLUE,
    3: Fore.YELLOW,
    4: Fore.GREEN,
}
def color_box(s, idx=0):
    """
    Function that creates a colored box based on the index passed in.
    """
    top_bar = '╭─{}─╮\n'.format(''.join(['─'] * len(s)))
    bottom_bar = '╰─{}─╯'.format(''.join(['─'] * len(s)))
    return '{}{}{}│ {} │\n{}{}'.format(Style.BRIGHT, switcher[idx], top_bar, s, bottom_bar, Style.RESET_ALL)


def colorize(s, idx=0):
    return '{}{}{}'.format(switcher[idx], s, Fore.WHITE)


# Internal strings
QMARK = '[{}?{}]'.format(Fore.YELLOW, Style.RESET_ALL)
invalid = lambda s: '{}{}{}'.format(Fore.RED, s, Style.RESET_ALL)
REMOVE_LINE = '\033[F'
CLEAR_TO_END = '\033[K'
