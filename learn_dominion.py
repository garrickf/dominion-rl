"""
Presents the implementaion for a harness to run Dominion experiments on!
"""
import argparse
import datetime
import os
import shutil

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
    format_str = 'python learn_dominion.py {}{} --niters {} --cache {}'
    comment = '-m "{}"'.format(desc) if desc else ''
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


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Run Dominon learning experiment.')
    parser.add_argument('-i', '--interactive', action='store_true', help='setup experiment in interactive mode')
    # parser.add_argument('--infile', '-i', default=DEFAULT_FILENAME, help='Name of data infile.')
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
    pass


def main():
    args = parse_args()
    # TODO: allow CLI/non-interactive mode
    if args.interactive or True: 
        settings = prompt_settings()
    else:
        # TODO: extract settings and confirm user wants them, otherwise abort
        pass
    
    # Make experiment directory and metafile
    path = settings['path']
    os.mkdir(path)
    write_metafile(path, settings)

    # TODO: run experiment given settings
    run_experiment(settings)


if __name__ == '__main__':
    main()
