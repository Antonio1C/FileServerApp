from importlib.metadata import entry_points
from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name = "FileServer007",
    version = '1.0.0.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires = [r for r in open(join(dirname(__file__), 'requirements.txt'), 'r') if '#' not in r],
    package_data={
        '': ['*.yaml', '*.ini']
    },
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest', 'mock', 'pytest-mock'],
    entry_points = {
        'console_sripts': ['fileserver007 = src.fileserver007:app']
    }
)