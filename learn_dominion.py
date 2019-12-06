"""
Presents the implementaion for a harness to run Dominion experiments on!
"""
import argparse
import datetime
import os
import shutil
import time         # For timing training
import pickle
import numpy as np

from util import strip_style
from policy import QLearningPolicy, RandomPolicy
from computer_player import ComputerPlayer
from game import Dominion
from utilities.filelog import FileLog

CWD = os.getcwd()

def namespace(experiment_name):
    """
    Translates an experiment name into a string that will be used to generate
    a directory and namespace data associated with that experiment.
    """
    # now = datetime.datetime.now()
    # return 'exp_{}_date{}_time{}-{}'.format(experiment_name, now.date(), now.hour, now.minute)
    return 'exp_{}'.format(experiment_name)


def manual_cmd_str(name, desc, n_iters, test_every, levels):
    """
    Returns a string representation of the manual command to run an experiment
    with given parameters.
    """
    format_str = 'python learn_dominion.py --name {}{} --niters {} --testevery {} --levels {}'
    comment = ' -m "{}"'.format(desc) if desc else ''
    return format_str.format(name, comment, n_iters, test_every, levels)


def write_metafile(dir, settings):
    """
    Writes a metafile containing information for the experiment to its respective
    directory.
    """
    filename = os.path.join(dir, 'meta.txt')
    with open(filename, 'w') as f:
        name = settings['name']
        desc = settings['desc']
        niters = settings['niters']
        testevery = settings['testevery']
        levels = settings['levels']

        f.write('Name: {}\n'.format(name))
        f.write('Description: {}\n'.format(desc))

        now = datetime.datetime.now()
        when = '{} {}:{}'.format(now.date(), now.hour, now.minute)
        f.write('Created: {}\n'.format(when))

        f.write('Iters: {}\n'.format(niters))
        f.write('Test/cache weights every: {}\n'.format(testevery))

        f.write('Cmd string:\n\t{}\n'.format(manual_cmd_str(name, desc, niters, testevery, levels)))
        f.close()


def write_game_log(dir, game_log, iter, info):
    """
    Writes a game log, indexed by the maturity (in iters) of the policy and the 
    string info (e.g., win or lose). Useful to see deveopment of strategies.
    """
    filename = os.path.join(dir, 'game_{}_iter{}.txt'.format(info, iter))
    if os.path.exists(filename): return # Already wrote one!
    with open(filename, 'w') as f:
        f.write(strip_style(game_log))
        f.close()


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Run Dominon learning experiment.')
    parser.add_argument('--name', help='experiment name')
    parser.add_argument('-m, --message', default='', dest='message', help='comments on experiment/description')
    parser.add_argument('-i', '--interactive', action='store_true', help='setup experiment in interactive mode')
    parser.add_argument('--niters', type=int, default=100, help='number of iterations to train for')
    parser.add_argument('--testevery', type=int, default=50, help='how often to test the policy')
    parser.add_argument('--levels', type=int, default=0, help='number of CPU levels to train against, tournament-style')
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
        levels = get_integer('Number of levels/brackets? 0 for normal iterative.')
        iters = get_integer('Number of training iters/games?')
        test_every = get_integer('Test agent every n games. n?')

        print('Brackets:\t{}\nIters\t{}\nTest Every:\t{} games'.format(levels, iters, test_every))

        okay = get_yes_or_no('OK?')
    
    print('To run this experiment again directly from the command line, run:\n\n\t{}\n'.format(manual_cmd_str(name, desc, iters, test_every, levels)))

    return {
        'path': path,
        'name': name,
        'desc': desc,
        'niters': iters,
        'testevery': test_every,
        'levels': levels
    }
    # TODO: verbosity, save game logs (?), discount factor ...


def run_bracket_experiment(settings):
    levels = settings['levels']
    path = settings['path']
    best_policy = bracket(levels, settings)
    dump_weights(path, best_policy.get_weights(), levels) # Dump the best policy


def bracket(n, settings):
    if n == 0:
        # Play against a random policy
        policy = QLearningPolicy()
        players = [ComputerPlayer(1, policy=policy), ComputerPlayer(2, policy=RandomPolicy())]
        best_policy = compete(players, settings, n)
        return best_policy

    # Make two level n-1 brackets
    best_policy_1 = bracket(n-1, settings)
    best_policy_2 = bracket(n-1, settings)

    players = [ComputerPlayer(1, policy=best_policy_1), ComputerPlayer(2, policy=best_policy_2)]
    best_policy = compete(players, settings, n)
    return best_policy


def compete(players, settings, n):
    niters = settings['niters']
    test_every = settings['testevery']
    path = settings['path']
    levels = settings['levels']

    # Helper function for timing
    elapsed = lambda tick, tock: time.strftime('%H:%M:%S', time.gmtime(tock - tick))
        
    print('Competition for a {}-level bracket!'.format(n))
    tick = time.time()
    wins = [0, 0]
    for i in range(niters):
        # Create and simulate a game
        game = Dominion(with_players=players, silence_output=True)        

        winner_idx, scores = game.play()
        wins[winner_idx] += 1
        tock = time.time()
        write_game_log(path, game.get_log(), i, '{}-level'.format(n))
        
        print('Iter: {}, winner: {}, scores: {}, {} elapsed'.format(i, winner_idx, scores, elapsed(tick, tock)))

    if n == 0:
        # First player always advances
        return players[0].policy

    winner_idx = np.argmax(wins)
    print('Player {} advances!'.format(winner_idx + 1))
    return players[winner_idx].policy # Return best player's policy


def dump_policy_losses(path, policy, i):
    """
    Dumps policy losses.
    """
    filename = os.path.join(path, '{}-iter{}.txt'.format(policy.file.filename, i))
    policy.file.dump_to(filename)


def dump_weights(path, policy, i):
    """
    Dumps policy losses.
    """
    filename = os.path.join(path, 'weights-iter{}.hdf5'.format(i))
    policy.save_weights(filename)


def run_experiment(settings):
    """
    Runs the specified experiment.
    """
    niters = settings['niters']
    test_every = settings['testevery']
    path = settings['path']
    testiters = 1
    # TODO: add verbose, cache every (?), log games on test (?), discount (?)

    # Create QLearningPolicy
    policy = QLearningPolicy(instanced=True, fileid=1)
    policy_clone = QLearningPolicy(instanced=True, fileid=2)
    assert(policy.model == policy_clone.model) # Should be same ref

    # Helper function for timing
    elapsed = lambda tick, tock: time.strftime('%H:%M:%S', time.gmtime(tock - tick))

    def test_policy(train_iter):
        """
        Helper to run_experiment that computes the win rate of the current policy
        against another computer opponent.
        """
        print('Testing...')
        policy.set_train(False)
        wins = 0
        tick = time.time()
        for i in range(testiters):
            # Play against a random policy opponent
            players = [ComputerPlayer(1, policy=policy), ComputerPlayer(2, policy=RandomPolicy())]
            game = Dominion(with_players=players, silence_output=True)
            winner_idx, scores = game.play()
            print('win idx:', winner_idx, scores)
            if winner_idx == 0:
                wins += 1
                write_game_log(path, game.get_log(), train_iter, 'win')
            else:
                write_game_log(path, game.get_log(), train_iter, 'lose')
            
        tock = time.time()
        print('(test_policy) {}% win rate (eval in: {})'.format(wins / testiters * 100, elapsed(tick, tock)))
        policy.set_train(True)
        return wins / testiters
        
    # test_policy(0)
    tick = time.time()
    for i in range(niters):
        # Create and simulate a game with itself
        players = [ComputerPlayer(1, policy=policy), ComputerPlayer(2, policy=policy_clone)]
        game = Dominion(with_players=players, silence_output=True)        

        winner_idx, scores = game.play()
        tock = time.time()
        # print(game.get_log())
        format_str = '> [{:3}]: P{} won {} to {} in {} rounds ({} elapsed)'
        rounds = game.game_info.rounds
        print(format_str.format(i, winner_idx+1, *sorted(scores, reverse=True), rounds, elapsed(tick, tock)))

        # Dump policy losses for each iter
        dump_policy_losses(path, policy, i)

        if ((i + 1) % test_every == 0):
            test_policy(i)
            dump_weights(path, policy, i)
            print('Dumped weights.')


def main():
    """
    Extract args and begin experiment.
    """
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
            'levels': args.levels,
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

    levels = settings['levels']
    if levels == 0:
        run_experiment(settings) # Can now beat a random opponent in a fixed game!
    else: 
        run_bracket_experiment(settings)


if __name__ == '__main__':
    main()
