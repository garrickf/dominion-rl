# Dominion!

To run a game and test: `python game.py`

## TODO

- Create a computer class that wraps around the player and can override inputs with its own policy and extract state information and valid action space information.
- Actions are relatively uniform when purchasing cards, but not in the middle of playing some actions. This is something to consider. (For example, the action space of a Mine when you have no treasure in your hand is only to abort the action! These 'worthless' plays ought to be penalized in some way.)

## Setting up dependencies

Some libraries like `numpy` may need installation on your machine; these dependencies are held in `requirements.txt`. One can use `venv` in Python 3 to set up a virtual environment like so:

```shell
python3 -m venv env
source venv/bin/activate
pip install -r requirements.txt
```

`venv` is just the name of the environment and can be substituted for anything you want, although only `venv` is ignored in the `git` configuation for the repo. Be careful not to commit locally installed libraries!

## Running experiments

To begin running experiments, the easiest thing to do is to mock one up in interactive mode. Run:

```shell
python learn_dominion.py -i
```

and you'll be taken through a series of questions to set up your experiment and the variables/hyperparameters therein. Interactive mode will tell you how to run those experiments again using just the CLI; for those of you who want to skip ahead:

```
usage: learn_dominion.py [-h] [-i]

Run Dominon learning experiment.

optional arguments:
  -h, --help         show this help message and exit
  -i, --interactive  setup experiment in interactive mode
```

## More Documention coming soon...