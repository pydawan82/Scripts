import subprocess as sp
import sys
import time
from argparse import ArgumentParser
from contextlib import contextmanager, redirect_stdout
from typing import Any, Callable, List, Tuple

from .file_wrapper import clear_end_of_line

CSI = '\x1b['
ALT_SCR = CSI + '?1049h'
NRM_SCR = CSI + '?1049l'
ED_END = CSI + '0J'
ED_ALL = CSI + '2J'
CUP_00 = CSI + 'H'

SCP = CSI + 's'
RCP = CSI + 'u'


@contextmanager
def alternate_screen():
    print(ALT_SCR, end='')

    try:
        yield
    finally:
        print(NRM_SCR, end='')


@contextmanager
def hide_cursor():
    print(CSI + '?25l', end='')

    try:
        yield
    finally:
        print(CSI + '?25h', end='')


def parse_args(args: List[str]) -> Tuple[List[str], float]:
    parser = ArgumentParser('watch')
    parser.add_argument(
        '-n', type=float, help='Delay in seconds, default 1s', default=1.0)
    parser.add_argument('command', nargs='+')
    ns = parser.parse_args(args)
    return ns.command, ns.n


def display(command: Callable[[], Any], delay: float):
    print(CUP_00, end='')
    command()
    print(ED_END, end='')


def watch(command: Callable[[], Any], delay: float):
    with alternate_screen():
        with hide_cursor():
            with redirect_stdout(clear_end_of_line(sys.stdout)):
                while True:
                    display(command, delay)
                    time.sleep(delay)


def main():
    command, delay = parse_args(sys.argv[1:])
    watch(lambda: sp.run(command), delay)


if __name__ == '__main__':
    main()
