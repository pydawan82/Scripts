import argparse
import sys
from dataclasses import dataclass
from functools import partial
from numbers import Number
from typing import List, Optional

import cpuinfo
import GPUtil as gputil
import psutil

from . import watch

from matplotlib import cm

def from_cm(cm_name: str, value: float) -> str:
    cmap = cm.get_cmap(cm_name)
    r, g, b, a = (int(c*255) for c in cmap(value))
    return f'38;2;{r};{g};{b}'

def temp_color(temp: float) -> str:
    if temp is None:
        return '97'

    return from_cm('cool', temp / 100)


def utilization_color(utilization: float) -> str:
    return from_cm('plasma', utilization)


def progress_bar(
    value: float, max_value: float = 1,
    length: int = 20,
    char: str = '━', style: str = None,
    empty_char: str = '━', empty_style='0'
) -> str:
    if style is None:
        style = utilization_color(value / max_value)
    complete_length = round(value / max_value * length)
    empty_length = length - complete_length
    rest = (value / max_value * length) % 1

    bar = char * complete_length
    empty_bar = empty_char * empty_length
    if bar and rest > 0.5:
        bar = bar[:-1] + '╸'
    elif empty_bar:
        empty_bar = '╺' + empty_bar[1:]

    return f'\033[{style}m{bar}\033[{empty_style}m{empty_bar}\033[0m'

def formatted(value: Optional[Number], format: str) -> str:
    if value is None:
        return 'N/A'
    return format % value

def percent(value: float) -> str:
    return f'{int(value * 100):3d}%'

def ratio(value: float, max_value: float, decimal: int=0) -> str:
    max_value_str = f"%.{decimal}f" % max_value
    value_str = f"%{len(max_value_str)}.{decimal}f" % value
    return f'{value_str}/{max_value_str}'


def exp_decay_update(self, attr: str, value: Number, weight: float = 0.9) -> None:
    if hasattr(self, attr) and getattr(self, attr) is not None:
        value = getattr(self, attr) * weight + value * (1 - weight)
    setattr(self, attr, value)


@dataclass
class CpuInfo:
    frequency: float  # Hz
    ram: float  # B
    utilization: float   # Range: 0-1

    name: str = cpuinfo.get_cpu_info()['brand_raw']
    cores: int = psutil.cpu_count(logical=False)
    threads: int = psutil.cpu_count(logical=True)

    max_frequency: float = psutil.cpu_freq()[2] * 1e6  # Hz
    max_ram: float = psutil.virtual_memory().total  # B

    temperature: float = None  # °C

    def __init__(self) -> None:
        psutil.cpu_percent()
        self.update()

    def update(self) -> None:
        freq, *_ = psutil.cpu_freq()
        virtual_memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent()

        exp_decay_update(self, 'frequency', freq * 1e6)
        exp_decay_update(self, 'ram', virtual_memory.used)
        if hasattr(psutil, 'sensors_temperatures'):
            exp_decay_update(
                self, 'temperature',
                psutil.sensors_temperatures()[
                    'coretemp'][0].current
            )
        exp_decay_update(self, 'utilization', cpu_usage / 100)

    @property
    def temperature_info(self) -> str:
        return f"\x1b[{temp_color(self.temperature)}m{formatted(self.temperature, '%4.1f')}°C"

    @property
    def frequency_info(self) -> str:
        return f"{progress_bar(self.frequency, self.max_frequency)} {ratio(self.frequency/1e9, self.max_frequency/1e9, 2)} GHz"


    @property
    def ram_info(self) -> str:
        return f"{progress_bar(self.ram, self.max_ram)} {ratio(self.frequency/2**30, self.max_frequency/2**30, 2)} GB"
    
    @property
    def utilization_info(self) -> str:
        return f"{progress_bar(self.utilization)} {percent(self.utilization)}"


    def __str__(self) -> str:
        return f"""\
\x1b[1;4;37m{self.name}\x1b[0m
\x1b[1;37mCores       \x1b[0m{self.cores}
\x1b[1;37mThreads     \x1b[0m{self.threads}
\x1b[1;37mTemperature \x1b[0m{self.temperature_info}\x1b[0m
\x1b[1;37mFrequency   \x1b[0m{self.frequency_info}\x1b[0m
\x1b[1;37mRAM         \x1b[0m{self.ram_info}\x1b[0m
\x1b[1;37mUtilization \x1b[0m{self.utilization_info}\x1b[0m\
"""


@dataclass
class GpuInfo:
    _index: int

    name: str
    max_ram: float

    ram: float
    temperature: float
    utilization: float

    def __init__(self, index, gpu) -> None:
        self._index = index
        self.name = gpu.name
        self.max_frequency = 2.3e9
        self.max_ram = gpu.memoryTotal * 2**20
        self.update()

    def update(self) -> None:
        gpu = gputil.getGPUs()[self._index]

        self.frequency = 0.5e9
        exp_decay_update(self, 'ram', gpu.memoryUsed * 2**20)
        exp_decay_update(self, 'temperature', gpu.temperature)
        exp_decay_update(self, 'utilization', gpu.load)

    @staticmethod
    def all() -> List['GpuInfo']:
        return [GpuInfo(i, gpu) for i, gpu in enumerate(gputil.getGPUs())]

    @property
    def temperature_info(self) -> str:
        return f"\x1b[{temp_color(self.temperature)}m{formatted(self.temperature, '%4.1f')}°C"

    @property
    def ram_info(self) -> str:
        return f"{progress_bar(self.ram, self.max_ram)} {ratio(self.ram/2**30, self.max_ram/2**30, 2)} GB"

    @property
    def utilization_info(self) -> str:
        return f"{progress_bar(self.utilization)} {percent(self.utilization)}"

    def __str__(self) -> str:
        return f"""\
\x1b[1;4;37m{self.name}\x1b[0m
\x1b[1;37mTemperature \x1b[0m{self.temperature_info}\x1b[0m
\x1b[1;37mRAM         \x1b[0m{self.ram_info}\x1b[0m
\x1b[1;37mUtilization \x1b[0m{self.utilization_info}\x1b[0m\
"""


def display_info(cpus: List[CpuInfo], gpus: List[GpuInfo]) -> None:

    for cpu in cpus:
        cpu.update()
        print(cpu)

    for gpu in gpus:
        gpu.update()
        print(gpu)


def parse_args(args: List[str]) -> float:
    parse = argparse.ArgumentParser()
    parse.add_argument('-n', type=float, default=1,
                       help='Update interval in seconds')

    return parse.parse_args(args).n


def main():
    interval = parse_args(sys.argv[1:])

    cpus = [CpuInfo()]
    gpus = GpuInfo.all()

    try:
        with watch.hide_cursor():
            watch.watch(partial(display_info, cpus, gpus),
                        interval)
    except KeyboardInterrupt:
        ...


if __name__ == '__main__':
    main()
