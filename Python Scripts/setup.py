from setuptools import setup

setup(
    name='watch',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'watch=watch:main'
        ]
    }
)


