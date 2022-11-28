EL_END = '\x1b[0K\n'

class clear_end_of_line:
    def __init__(self, file):
        self.file = file

    def write(self, s:str):
        s = s.replace('\n', EL_END)
        self.file.write(s)