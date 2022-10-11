from setuptools import setup

setup(
    name='pdwnutil',
    version='0.0.2',
    entry_points={
        'console_scripts': [
            'watch=pdwnutil.watch:main',
            'hw-info=pdwnutil.hw_info:main'
        ]
    },
    install_requires=['GPUtil', 'psutil', 'py-cpuinfo'],
)
