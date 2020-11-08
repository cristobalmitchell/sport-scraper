from os.path import dirname, join

from pkg_resources import parse_version
from setuptools import __version__ as setuptools_version, find_packages, setup


with open(join(dirname(__file__), "sport_scraper/VERSION"), "rb") as f:
    version = f.read().decode("ascii").strip()

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "pandas>=1.0",
    "bs4>=0.0.1",
]
extras_require = {}

setup(
    name="sport-scraper",
    version=version,
    author="Cristobal Mitchell",
    author_email="cristobalmitchell@gmail.com",
    description="Simple web scraper package for gathering sports data from ESPN.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cristobalmitchell/sports-scraper",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_require,
)
