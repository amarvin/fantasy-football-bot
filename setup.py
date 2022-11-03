from io import open
from os import path

from setuptools import find_packages, setup

from ffbot.constants import VERSION

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def get_requirements(kind: str = None):
    if kind:
        filename = f"requirements-{kind}.txt"
    else:
        filename = "requirements.txt"
    with open(filename) as f:
        requires = (line.strip() for line in f)
        return [req for req in requires if req and not req.startswith("#")]


setup(
    name="ffbot",
    version=VERSION,
    description="Automate playing Yahoo Fantasy Football",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amarvin/fantasy-football-bot",
    author="Alex Marvin",
    author_email="alex.marvin@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="fantasy-football bot yahoo",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.0",
    install_requires=get_requirements(),
    extra_require={
        "test": get_requirements("test"),
    },
)
