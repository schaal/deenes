#!/usr/bin/python3

from setuptools import setup

setup(
    name='Deenes',
    version='0.2',
    packages=['src'],
    entry_points={'console_scripts': ['deenes = src.deenes:main']},
    install_requires=[
        'pyroute2',
        'systemd-python',
        'IPy',
        'pyxdg',
        'requests',
        'requests-mock',
        'tenacity'
    ],
    test_suite='tests'
)
