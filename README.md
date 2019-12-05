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

## More Documention coming soon...