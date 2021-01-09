"""Play a two player game.
"""
# From dominion module
import dominion.util.logging as logging
from dominion.game import Game

logging.configure_time()
logging.silence_console_output()

game = Game()
game.play()
