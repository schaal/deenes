from setuptools import setup

setup(
    name='Deenes',
    version='0.1',
    packages=['src'],
    entry_points={'console_scripts': ['deenes = src.deenes:main']},
    install_requires=[
        'pyroute2',
        'systemd-python',
        'IPy',
        'pyxdg'
    ],
    test_suite='tests'
)