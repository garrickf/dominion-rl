# Dominion!

> Final project developed for CS238: Decision Making Under Uncertainty, Autumn 2019, by @garrickf and @andersonbcdefg.

Presents a game simulator for the deck-building game *Dominion* (built in Python) and a deep reinforcement learning algorithm which develops strategies for the game (written in Keras/Python).

Read our paper [here!](http://stanford.edu/~banders9/dominion.pdf)

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
usage: learn_dominion.py [-h] [--name NAME] [-m, --message MESSAGE] [-i]
                         [--niters NITERS] [--testevery TESTEVERY]
                         [--levels LEVELS]

Run Dominon learning experiment.

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           experiment name
  -m, --message MESSAGE
                        comments on experiment/description
  -i, --interactive     setup experiment in interactive mode
  --niters NITERS       number of iterations to train for
  --testevery TESTEVERY
                        how often to test the policy
  --levels LEVELS       number of CPU levels to train against, tournament-
                        style
```

## Playing a game of Dominion

To play Dominion against a computer agent, run

```shell
python game.py [weightfile]
```

where `weightfile` is the path to a weightfile that gets loaded into the neural
network.

> 2-player human games, fixed and random policies coming soon...

## More Documention coming soon...