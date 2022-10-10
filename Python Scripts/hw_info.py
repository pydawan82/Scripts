from dataclasses import dataclass
import sys
import subprocess as sp

from wmic import wmic_get

def temp_color(temp: float) -> str:
    if temp < 30:
        return "96"
    elif temp < 40:
        return "92"
    elif temp < 50:
        return "93"
    elif temp < 60:
        return "33"
    elif temp < 70:
        return "31"
    else:
        return "91"

def utilization_color(utilization: float) -> str:
    if utilization < 0.2:
        return "96"
    elif utilization < 0.4:
        return "92"
    elif utilization < 0.6:
        return "93"
    elif utilization < 0.8:
        return "33"
    else:
        return "91"

def progress_bar(
    value: float, max_value: float = 1,
    length: int = 20,
    char: str = "━", style: str = None,
    empty_char: str="━", empty_style = "0"
    ) -> str:
    if style is None:
        style = utilization_color(value / max_value)
    return f"\033[{style}m{char * int(value / max_value * length)}\033[{empty_style}m{empty_char * (length - int(value / max_value * length))}\033[0m"

@dataclass(frozen=True)
class CpuInfo:
    name: str
    cores: int
    threads: int
    max_frequency: float # Hz
    max_ram: float # B

    frequency: float # Hz
    ram: float # B
    temperature: float
    utilization: float

    def __str__(self) -> str:
        return f"""\
\x1b[1;37m{self.name}\x1b[0m
\x1b[1;37mCores:\x1b[0m {self.cores}
\x1b[1;37mThreads:\x1b[0m {self.threads}
\x1b[1;37mTemperature: \x1b[0m\x1b[{temp_color(self.temperature)}m{self.temperature:04.1f}°C\x1b[0m
\x1b[1;37mFrequency:   \x1b[0m{progress_bar(self.frequency, self.max_frequency)} {self.frequency / 1e9:.2f}/{self.max_frequency / 1e9:.2f} GHz
\x1b[1;37mRAM:         \x1b[0m{progress_bar(self.ram, self.max_ram)} {self.ram / 1e9:.2f}/{self.max_ram / 1e9:.2f} GB
\x1b[1;37mUtilization: \x1b[0m{progress_bar(self.utilization)} {self.utilization*100:.0f}%"""


@dataclass(frozen=True)
class GpuInfo:
    name: str
    max_frequency: float
    max_ram: float

    frequency: float
    ram: float
    temperature: float
    utilization: float

    def __str__(self) -> str:
        return f"""\
\x1b[1;37m{self.name}\x1b[0m
\x1b[1;37mTemperature: \x1b[0m\x1b[{temp_color(self.temperature)}m{self.temperature:04.1f}°C\x1b[0m
\x1b[1;37mFrequency:   \x1b[0m{progress_bar(self.frequency, self.max_frequency)} {self.frequency / 1e9:.2f}/{self.max_frequency / 1e9:.2f} GHz
\x1b[1;37mRAM:         \x1b[0m{progress_bar(self.ram, self.max_ram)} {self.ram / 1e9:.2f}/{self.max_ram / 1e9:.2f} GB
\x1b[1;37mUtilization: \x1b[0m{progress_bar(self.utilization)} {self.utilization*100:.0f}%"""

def cpu_info() -> CpuInfo:
    cpu = wmic_get("cpu")[0]
    ram = wmic_get("memorychip")[0]
    temp = wmic_get("temperature")
    temp = next(filter(lambda x: x.description == "CPU", temp), None)
    return CpuInfo(
        name=cpu.name,
        cores=int(cpu.numberofcores),
        threads=int(cpu.numberoflogicalprocessors),
        max_frequency=float(cpu.maxclockspeed) * 1e6,
        max_ram=float(ram.capacity) / 1.024**3,
        frequency=float(cpu.currentclockspeed) * 1e6,
        ram=7.8e9,
        temperature=temp,
        utilization=float(cpu.loadpercentage) / 100,
    )

def gpu_info() -> list[GpuInfo]:
    gpus = wmic_get("path win32_VideoController")

    return [GpuInfo(
        name=gpu.name,
        max_frequency= 2.3e9,
        max_ram=float(gpu.adapterRam) / 1.024**3,
        frequency=1.8e9,
        ram=0.8e9,
        temperature=59.7,
        utilization=0.83,
    ) for gpu in gpus]


def main():
    args = sys.argv[1:]
    print(cpu_info())
    print()

    for gpu in gpu_info():
        print(gpu)
        print()

if __name__ == '__main__':
    main()