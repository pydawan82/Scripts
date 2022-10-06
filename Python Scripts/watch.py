from contextlib import contextmanager
import subprocess as sp
import sys
import time
from argparse import ArgumentParser

CSI = '\x1b['
ALT_SCR = CSI + '?1049h'
NRM_SCR = CSI + '?1049l'
CLR_END = CSI + '0J'
CLR_SCR = CSI + '2J'
CRS_TOPLEFT = CSI + 'H'

@contextmanager
def alternate_screen():
    print(ALT_SCR)
    
    try:
        yield
    finally:
        print(NRM_SCR)


def parse_args(args: list[str]) -> tuple[list[str], float, bool]:
    parser = ArgumentParser('watch')
    parser.add_argument('-n', type=float, help='Delay in seconds, default 1s', default=1.0)
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


def watch_safe(command: list[str], delay: float):
    try:
        while True:
            print(CRS_TOPLEFT + CLR_SCR)
            sp.run(command, check=True)
            time.sleep(delay)
    except KeyboardInterrupt:
        ...

def watch(command: list[str], delay: float):
    try:
        while True:
            print(CRS_TOPLEFT)
            sp.run(command, check=True)
            print(CLR_END)
            time.sleep(delay)
    except KeyboardInterrupt:
        ...


def main(args: list[str]):
    command, delay, safe = parse_args(args)

    watch_fn = watch_safe if safe else watch

    with alternate_screen():
        watch_fn(command, delay)


if __name__ == '__main__':
    main(sys.argv[1:])
