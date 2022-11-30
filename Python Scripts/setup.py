from setuptools import setup
import os

scripts = [
    'hw-info=pdwnutil.hw_info:main',
]

if os.name == 'nt':
    scripts += [
        'watch=pdwnutil.watch:main'
        ]

setup(
    name='pdwnutil',
    version='0.0.4',
    entry_points={
        'console_scripts': scripts
    },
    install_requires=['GPUtil', 'psutil', 'py-cpuinfo'],
)
