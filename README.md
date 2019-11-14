# Dominion!

To run a game and test: `python game.py`

## TODO

- Create a computer class that wraps around the player and can override inputs with its own policy and extract state information and valid action space information.
- Actions are relatively uniform when purchasing cards, but not in the middle of playing some actions. This is something to consider. (For example, the action space of a Mine when you have no treasure in your hand is only to abort the action! These 'worthless' plays ought to be penalized in some way.)