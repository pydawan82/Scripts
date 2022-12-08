from typing import TextIO

END = '\x1b[0K'
EL_END = '\x1b[0K\n'

class clear_end_of_line:
    """
    A wrapper for a file-like object that writes a clear end of line
    escape sequence before each newline.

    Behaviour with MS-DOS ('\\r\\n') line endings is undefined.
    """
    def __init__(self, file: TextIO):
        self.file = file

    def write(self, s: str, /) -> int:
        count = s.count(END)
        s = s.replace(END, EL_END)
        return self.file.write(s) + count * (len(EL_END) - len(END))