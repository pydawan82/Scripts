import argparse
import sys
from dataclasses import dataclass
from functools import partial
from math import ceil
from numbers import Number
from typing import List

import cpuinfo
import GPUtil as gputil
import psutil

import pdwnutil.watch as watch


def temp_color(temp: float) -> str:
    if temp is None:
        return '95'
    if temp < 30:
        return '96'
    elif temp < 40:
        return '92'
    elif temp < 50:
        return '93'
    elif temp < 60:
        return '33'
    elif temp < 70:
        return '31'
    else:
        return '91'


def utilization_color(utilization: float) -> str:
    if utilization < 0.2:
        return '96'
    elif utilization < 0.4:
        return '92'
    elif utilization < 0.6:
        return '93'
    elif utilization < 0.8:
        return '33'
    else:
        return '91'


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

    def __str__(self) -> str:
        return f"""\
\x1b[1;4;37m{self.name}\x1b[0m
\x1b[1;37mCores       \x1b[0m{self.cores}
\x1b[1;37mThreads     \x1b[0m{self.threads}
\x1b[1;37mTemperature \x1b[0m\x1b[{temp_color(self.temperature)}m{('%04.1f' % (self.temperature,)) if self.temperature is not None else 'N/A'}°C\x1b[0m
\x1b[1;37mFrequency   \x1b[0m{progress_bar(self.frequency, self.max_frequency)} {self.frequency / 1e9:4.2f}/{self.max_frequency / 1e9:4.2f} GHz
\x1b[1;37mRAM         \x1b[0m{progress_bar(self.ram, self.max_ram)} {self.ram / 2**30:5.2f}/{self.max_ram / 2**30:5.2f} GB
\x1b[1;37mUtilization \x1b[0m{progress_bar(self.utilization)} {self.utilization*100:3.0f}%"""


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

    def __str__(self) -> str:
        return f"""\
\x1b[1;4;37m{self.name}\x1b[0m
\x1b[1;37mTemperature \x1b[0m\x1b[{temp_color(self.temperature)}m{self.temperature:04.1f}°C\x1b[0m
\x1b[1;37mRAM         \x1b[0m{progress_bar(self.ram, self.max_ram)} {self.ram / 2**30:5.2f}/{self.max_ram / 2**30:5.2f} GB
\x1b[1;37mUtilization \x1b[0m{progress_bar(self.utilization)} {self.utilization*100:3.0f}%"""


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
                        interval, safe=False)
    except KeyboardInterrupt:
        ...


if __name__ == '__main__':
    main()
