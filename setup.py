# setup.py - Setup script
from setuptools import setup, find_packages

setup(
    name="xtaagc-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open("requirements.txt").readlines()
    ],
    author="XTAAGC Team",
    description="Advanced Crypto Trading Bot",
    python_requires=">=3.9",
)