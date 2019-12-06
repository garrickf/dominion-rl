import os

class Console:
    """
    The singleton class console wraps the print function for anything
    under the game. This lets us imperatively silence all game output if we want
    to (for example, when training a computer to play).
    """
    class __Console:
        def __init__(self):
            self.verbose = True


    instance = None
    @staticmethod
    def __get_instance():
        if not Console.instance:
            Console.instance = Console.__Console()

        return Console.instance


    @staticmethod
    def log(str):
        curr_instance = Console.__get_instance()
        if curr_instance.verbose:
            print(str)


    @staticmethod
    def clear():
        curr_instance = Console.__get_instance()
        if curr_instance.verbose:
            os.system('clear')


    @staticmethod
    def set_verbose(is_verbose):
        curr_instance = Console.__get_instance()
        curr_instance.verbose = is_verbose
