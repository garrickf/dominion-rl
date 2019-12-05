class Log:
    """
    The game log stores messages that relate the status of the game.
    Singleton class; defines and manages an instance of a private inner class.
    """
    class __Log:
        def __init__(self):
            self.messages = []
            self.verbose = True


        @property
        def recent(self):
            NUM_MESSAGES_TO_DISPLAY = 11
            recent = self.messages[-NUM_MESSAGES_TO_DISPLAY:]
            return '...\n' + '\n'.join(recent)


        @property
        def full(self):
            return '\n'.join(self.messages)


        def add_message(self, m, suppress_output=False):
            if not suppress_output and self.verbose:
                print(m)
            self.messages.append(m)

        
        def set_verbose(self, is_verbose):
            """
            Sets verbosity of logger. If False (silent), messages sent to the log
            are not printed to stdout.
            """
            self.verbose = is_verbose
        
        
        def __str__(self):
            return repr(self)


    instance = None
    def __init__(self):
        if not Log.instance:
            Log.instance = Log.__Log()
    

    def __getattr__(self, name):
        """
        Functions are attributes too: class.fn_attr(*args)
        """
        return getattr(self.instance, name)

# Testing code
# log = Log()
# log.add_message('Hello world')
# print(log.recent)
