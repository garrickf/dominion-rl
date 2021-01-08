"""The logging module handles console output and logging to multiple files: one
for the game transcript, one for the full game log (including card information),
and player logs (what each player "sees").
"""

# Python stdlib
import logging
import os
import re
from datetime import datetime, timezone
from typing import List, MutableMapping, Sequence, Union

# From dominion module
from dominion.common import LogTarget
from utilities.log import Log

targetsT = Union[List[Union[LogTarget, str]], LogTarget, str]

# Configure the root logger to emit all logging messages with severity DEBUG or
# higher, and get rid of parent handlers. Child loggers will have handlers.
logging.basicConfig(level=logging.DEBUG, handlers=[])

now = datetime.now(timezone.utc)
dir_path = f"run_{now.strftime('%Y-%m-%d_%H-%M-%S')}"


# 7-bit C1 ANSI sequences
ansi_escape = re.compile(
    r"""
        \x1B    # ESC
        [@-_]   # 7-bit C1 Fe
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    """,
    re.VERBOSE,
)


def strip_style(text):
    """Strips ANSI escape sequences that colorama adds. Adapted from Stack Overflow:
    https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    """
    return ansi_escape.sub("", text)


class NoColorFormatter(logging.Formatter):
    def __init__(self):
        pass

    def format(self, record):
        return strip_style(record.msg)


def getLogger(
    name: str, to_console: bool = False, to_file: bool = True
) -> logging.Logger:
    """Adapter for logging.getLogger and adding handlers"""
    # Create the logging directory if it doesn't exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    logger = logging.getLogger(name)

    if to_console:
        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)

    if to_file:
        file_path = f"{name}.log"
        file_handler = logging.FileHandler(os.path.join(dir_path, file_path))
        file_handler.setFormatter(NoColorFormatter())
        logger.addHandler(file_handler)

    return logger


# Globals keep instances of all loggers used
loggers: MutableMapping[LogTarget, logging.Logger] = {}
player_loggers: MutableMapping[str, logging.Logger] = {}
output_observer = True

def log(targets: targetsT, message: str):
    global loggers

    # Lazy initialize the loggers
    if not loggers:
        loggers = {
            LogTarget.GAME: getLogger("game"),
            LogTarget.OBSERVER: getLogger("observer", to_console=output_observer),
        }

    if not isinstance(targets, list):
        targets = [targets]

    for target in targets:
        if not isinstance(target, LogTarget):
            if target not in player_loggers:
                to_console = False if "CPU" in target else True
                target_name = (
                    target.lower().replace(" ", "-").replace("(", "").replace(")", "")
                )
                player_loggers[target] = getLogger(target_name, to_console=to_console)
            logger = player_loggers[target]
        else:
            logger = loggers[target]

        logger.info(message)

        if target == LogTarget.OBSERVER:
            # Apply log message to all players, since they see it too
            for logger in player_loggers.values():
                logger.info(message)


def silence_console_output() -> None:
    global output_observer
    output_observer = False


def configure_time() -> None:
    global dir_path
    global loggers
    global player_loggers

    now = datetime.now(timezone.utc)
    dir_path = f"run_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

    # Clear any previous loggers
    loggers = {}
    player_loggers = {}


# Make constants available from module
GAME = LogTarget.GAME
OBSERVER = LogTarget.OBSERVER
