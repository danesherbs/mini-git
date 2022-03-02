from setuptools import setup

setup(
    name="minigit",
    version="1.0",
    packages=["minigit"],
    entry_points={"console_scripts": ["minigit = minigit.cli:main"]},
)
