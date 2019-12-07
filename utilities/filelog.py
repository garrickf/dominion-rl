class FileLog:
    """
    Keeps singleton instances of files to be logged to, accessed by a dictionary.
    """

    class __FileLog:
        def __init__(self, key):
            self.lines = []
            self.filename = key
        
        
        def write(self, text):
            self.lines.append('{}\n'.format(text))


        def dump_to(self, filepath):
            with open(filepath, 'w') as f:
                f.write(''.join(self.lines))


    instances = {}
    @staticmethod
    def __get_instance(key):
        if key not in FileLog.instances:
            FileLog.instances[key] = FileLog.__FileLog(key)

        return FileLog.instances[key]


    @staticmethod
    def file(key):
        curr_instance = FileLog.__get_instance(key)
        return curr_instance
