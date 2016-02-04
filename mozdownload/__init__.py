# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

from mozdownload import cli
from mozdownload.factory import FactoryScraper
from mozdownload.scraper import (
    Scraper,
    DailyScraper,
    DirectScraper,
    ReleaseScraper,
    ReleaseCandidateScraper,
    TinderboxScraper,
    TryScraper,
)

__version__ = '1.19'

__all__ = [
    __version__,
    cli,
    FactoryScraper,
    Scraper,
    DailyScraper,
    DirectScraper,
    ReleaseScraper,
    ReleaseCandidateScraper,
    TinderboxScraper,
    TryScraper,
]
