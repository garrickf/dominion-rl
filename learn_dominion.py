"""
Presents the implementaion for a harness to run Dominion experiments on!
"""
import argparse
import datetime
import os
import shutil
import time         # For timing training

from util import strip_style
from policy import QLearningPolicy, RandomPolicy
from computer_player import ComputerPlayer
from game import Dominion

CWD = os.getcwd()

def namespace(experiment_name):
    """
    Translates an experiment name into a string that will be used to generate
    a directory and namespace data associated with that experiment.
    """
    # now = datetime.datetime.now()
    # return 'exp_{}_date{}_time{}-{}'.format(experiment_name, now.date(), now.hour, now.minute)
    return 'exp_{}'.format(experiment_name)


def manual_cmd_str(name, desc, n_iters, test_every):
    """
    Returns a string representation of the manual command to run an experiment
    with given parameters.
    """
    format_str = 'python learn_dominion.py {}{} --niters {} --testevery {}'
    comment = ' -m "{}"'.format(desc) if desc else ''
    return format_str.format(name, comment, n_iters, test_every)


def write_metafile(dir, settings):
    """
    Writes a metafile containing information for the experiment to its respective
    directory.
    """
    filename = os.path.join(dir, 'meta.txt')
    with open(filename, 'w') as f:
        f.write('Name: {}\n'.format(settings['name']))
        f.write('Description: {}\n'.format(settings['desc']))

        now = datetime.datetime.now()
        when = '{} {}:{}'.format(now.date(), now.hour, now.minute)
        f.write('Created: {}\n'.format(when))

        f.write('Iters: {}\n'.format(settings['niters']))
        f.write('Test/cache weights every: {}\n'.format(settings['testevery']))
        f.close()


def write_game_log(dir, game_log, iter, state):
    """
    Writes a game log, indexed by the maturity (in iters) of the policy and the 
    string state (win or lose). Useful to see deveopment of strategies.
    """
    filename = os.path.join(dir, 'game_{}_iter{}.txt'.format(state, iter))
    if os.path.exists(filename): return # Already wrote one!
    with open(filename, 'w') as f:
        f.write(strip_style(game_log))
        f.close()


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Run Dominon learning experiment.')
    parser.add_argument('name', help='experiment name')
    parser.add_argument('-m, --message', default='', dest='message', help='comments on experiment/description')
    parser.add_argument('-i', '--interactive', action='store_true', help='setup experiment in interactive mode')
    parser.add_argument('--niters', type=int, default=100, help='number of iterations to train for')
    parser.add_argument('--testevery', type=int, default=10, help='how often to test the policy')
    # parser.add_argument('--experiment', '-e', default=0, type=int, help='Experiment number.')
    # parser.add_argument('--test', '-t', action='store_true', help='Run test set (default: False).')
    # parser.add_argument('--save_weights', '-s', action='store_true', help='Save weights (default: False).')
    # parser.add_argument('--load_weights', '-w', help='Load weights from hdf5 file (default: None).')
    # parser.add_argument('--tmp_dir', '-dir', default='tmp', help='Temp dir to dump info (default: tmp).')

    return parser.parse_args()


def get_line(prompt):
    prompt = '[?] {} '.format(prompt)
    return input(prompt)


def get_integer(prompt):
    prompt = '[?] {} '.format(prompt)
    typed = input(prompt)
    if typed.isdigit():
        return int(typed)

    while True:
        print('Invalid input. Please type an integer.')
        typed = input(prompt)
        if typed.isdigit():
            return int(typed)


def get_yes_or_no(prompt):
    prompt = '[Y/N] {} '.format(prompt)
    typed = input(prompt)
    if typed and (typed.lower()[0] == 'y' or typed.lower()[0] == 'n'):
        return typed.lower()[0] == 'y'

    while True:
        print('Invalid input. Type something beginning with "y" or "n".')
        typed = input(prompt)
        if typed and (typed.lower()[0] == 'y' or typed.lower()[0] == 'n'):
            return typed.lower()[0] == 'y'


def prompt_settings():
    """
    Guides the user through setting up an experiment.
    """
    # Metadata setup (directory name, description)
    okay = False
    while not okay:
        print('Metadata setup:')
        name = get_line('Name of experiment?')
        desc = get_line('Description of experiment?')

        dir = namespace(name)
    
        print('Name\t{}\nDesc:\t{}\nDirectory:\t{}'.format(name, desc, dir))
        
        path = os.path.join(CWD, dir)
        if os.path.exists(path) and os.path.isdir(path):
            print('Warning: directory "{}" already exists and will be overwritten.'.format(dir))
        else:
            print('Directory "{}" will be created.'.format(dir))

        okay = get_yes_or_no('OK?')
    
    if os.path.exists(path) and os.path.isdir(path): # Remove folder if exists
        shutil.rmtree(path)

    # Experiment setup (niters, etc.)
    okay = False
    while not okay:
        print('Experiment setup:')
        iters = get_integer('Number of training iters/games?')
        test_every = get_integer('Test agent every n games. n?')

        print('Iters\t{}\nTest Every:\t{} games'.format(iters, test_every))

        okay = get_yes_or_no('OK?')
    
    print('To run this experiment again directly from the command line, run:\n\n\t{}\n'.format(manual_cmd_str(name, desc, iters, test_every)))

    return {
        'path': path,
        'name': name,
        'desc': desc,
        'niters': iters,
        'testevery': test_every,
    }
    # TODO: verbosity, save game logs (?), ...


def run_experiment(settings):
    """
    Runs the specified experiment.
    """
    niters = settings['niters']
    test_every = settings['testevery']
    path = settings['path']
    testiters = 100
    # TODO: add verbose, cache every (?), log games on test (?), discount (?)

    # Create QLearningPolicy
    # policy = QLearningPolicy() # TODO: fix QL policy and uncomment
    policy = RandomPolicy()

    # Helper function for timing
    elapsed = lambda tick, tock: time.strftime('%H:%M:%S', time.gmtime(tock - tick))

    def test_policy(train_iter):
        """
        Helper to run_experiment that computes the win rate of the current policy
        against another computer opponent.
        """
        wins = 0
        tick = time.time()
        for i in range(testiters):
            # Play against a random policy opponent
            players = [ComputerPlayer(1, policy=policy), ComputerPlayer(2, policy=RandomPolicy())]
            game = Dominion(with_players=players, silence_output=True)
            winner_idx, scores = game.play()
            # print(winner_idx, scores)
            if winner_idx == 0:
                wins += 1
                write_game_log(path, game.get_log(), train_iter, 'win')
            else:
                write_game_log(path, game.get_log(), train_iter, 'lose')
            
        tock = time.time()
        print('(test_policy) {}% win rate (eval in: {})'.format(wins / testiters * 100, elapsed(tick, tock)))
        return wins / testiters
        
    tick = time.time()
    for i in range(niters):
        # Create and simulate a game
        players = [ComputerPlayer(1, policy=policy), ComputerPlayer(2, policy=RandomPolicy())] # TODO: player could go first or second
        game = Dominion(with_players=players, silence_output=True)        

        winner_idx, scores = game.play()
        tock = time.time()
        # print(game.get_log())
        print('Iter: {}, winner: {}, scores: {}, {} elapsed'.format(i, winner_idx, scores, elapsed(tick, tock)))

        if ((i + 1) % test_every == 0):
            test_policy(i)


def main():
    args = parse_args()
    if args.interactive: 
        settings = prompt_settings()
    else:
        # Extract settings from args
        path = namespace(args.name)
        settings = {
            'name': args.name,
            'desc': args.message,
            'path': path,
            'niters': args.niters,
            'testevery': args.testevery,
        }

        if os.path.exists(path) and os.path.isdir(path):
            print('Warning: directory "{}" already exists and will be overwritten.'.format(path))

            if(get_yes_or_no('OK?')):
                shutil.rmtree(path) # Remove original directory
            else:
                print('Aborting.')
                exit()
    
    # Make experiment directory and metafile
    path = settings['path']
    os.mkdir(path)
    write_metafile(path, settings)

    # Run experiment given settings
    run_experiment(settings)


if __name__ == '__main__':
    main()
