from setuptools import setup

setup(
    name='hydws',
    packages=[''],
    entry_points={
        'console_scripts': [
            'hydws=hydws.cli:app'
        ],
    },
)
