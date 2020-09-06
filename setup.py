from io import open
from os import path
from setuptools import setup, find_packages

from ffbot.constants import VERSION


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ffbot',
    version=VERSION,
    description='Automate playing Yahoo Fantasy Football',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/amarvin/fantasy-football-bot',
    author='Alex Marvin',
    author_email='alex.marvin@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='fantasy-football bot yahoo',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.0',
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'pandas',
        'pulp',
        'requests',
        'tabulate',
        'user_agent',
    ],
)
