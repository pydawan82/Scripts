import subprocess as sp
import sys
import time
from argparse import ArgumentParser
from contextlib import contextmanager
from typing import Any, Callable, List, Tuple

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


def parse_args(args: List[str]) -> Tuple[List[str], float, bool]:
    parser = ArgumentParser('watch')
    parser.add_argument(
        '-n', type=float, help='Delay in seconds, default 1s', default=1.0)
    parser.add_argument('command', nargs='+')
    parser.add_argument('--safe', action='store_true',
                        help='''
    Clears screen before running command, might cause flickering.
    If not set, only the output after the cursor will be cleared after each run.
    This parameter should be set if the length of a line is not constant.
    '''
                        )
    ns = parser.parse_args(args)
    return ns.command, ns.n, ns.safe


def display_safe(command: list[str], delay: float):
    print(CUP_00 + ED_ALL, end='')
    command()


def display(command: Callable[[], Any], delay: float):
    print(CUP_00, end='')
    command()
    print(ED_END, end='')


def watch(command: Callable[[], Any], delay: float, safe=False):
    watch_fn = display_safe if safe else display

    with alternate_screen():
        with hide_cursor():
            while True:
                watch_fn(command, delay)
                time.sleep(delay)


def main():
    command, delay, safe = parse_args(sys.argv[1:])
    watch(lambda: sp.run(command), delay, safe)


if __name__ == '__main__':
    main()
