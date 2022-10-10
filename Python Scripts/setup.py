from setuptools import setup

setup(
    name='pydwn_utils',
    version='0.0.2',
    entry_points={
        'console_scripts': [
            'watch=watch:main',
            'hw_info=hw_info:main'
        ]
    },
    install_requires=['GPUtil', 'psutil', 'py-cpuinfo'],
)
