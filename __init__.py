"""
sportScraper - web scraping utility for gathering sports data from espn.com
"""

import pkgutil
import sys
import warnings

# Declare top-level shortcuts
from sport_scraper.base import SportScraper


__all__ = [
    "__version__",
    "version_info",
    "sportScraper",
]

# sportScraper version
__version__ = pkgutil.get_data(__package__, "VERSION").decode("ascii").strip()
version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split("."))

# Check minimum required Python version
if sys.version_info < (3, 6):
    print("sportScraper %s requires Python 3.6+" % __version__)
    sys.exit(1)


del pkgutil
del sys
del warnings
