#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import tempfile
import unittest
import urllib

import mozfile

import mozdownload
from mozdownload.scraper import BASE_URL
from mozdownload.utils import urljoin


tests_release_scraper = [
    # -p win32 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest'}},

    # -p win32 -v 52.0
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '52.0'},
     'url': 'thunderbird/releases/52.0/win32/en-US/Thunderbird Setup 52.0.exe'},

    # -p linux -v 52.0
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': '52.0'},
     'url': 'thunderbird/releases/52.0/linux-i686/en-US/thunderbird-52.0.tar.bz2'},

    # -a thunderbird -p linux64 -v 52.0
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': '52.0'},
     'url': 'thunderbird/releases/52.0/linux-x86_64/en-US/thunderbird-52.0.tar.bz2'},

    # -a thunderbird -p mac -v 52.0
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': '52.0'},
     'url': 'thunderbird/releases/52.0/mac/en-US/Thunderbird 52.0.dmg'},

    # -a thunderbird -p win32 -v 52.0 -l de
    {'args': {'application': 'thunderbird',
              'locale': 'de',
              'platform': 'win32',
              'version': '52.0'},
     'url': 'thunderbird/releases/52.0/win32/de/Thunderbird Setup 52.0.exe'},
]

tests_candidate_scraper = [
    # -a thunderbird -p linux -v 52.7.0
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/linux-i686/en-US/thunderbird-52.7.0.tar.bz2'},

    # -a thunderbird -p linux64 -v 52.7.0
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/linux-x86_64/en-US/thunderbird-52.7.0.tar.bz2'},

    # -a thunderbird -p mac -v 52.7.0
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/mac/en-US/Thunderbird 52.7.0.dmg'},

    # -a thunderbird -p win32 -v 52.7.0
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/win32/en-US/Thunderbird Setup 52.7.0.exe'},

    # -a thunderbird -p win32 -v 52.7.0 -l cs
    {'args': {'application': 'thunderbird',
              'locale': 'cs',
              'platform': 'win32',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/win32/cs/Thunderbird Setup 52.7.0.exe'},

    # -a thunderbird -p win32 -v 52.7.0 -l en-GB
    {'args': {'application': 'thunderbird',
              'locale': 'en-GB',
              'platform': 'win32',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/win32/en-GB/Thunderbird Setup 52.7.0.exe'},

    # -a thunderbird -p win32 -v 52.7.0
    {'args': {'application': 'thunderbird',
              'build_number': '1',
              'platform': 'win32',
              'version': '52.7.0'},
     'url': 'thunderbird/candidates/52.7.0-candidates/build1/win32/en-US/Thunderbird Setup 52.7.0.exe'},
]

tests_daily_scraper = [
    # -p linux --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central'}},

    # -p linux64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'branch': 'comm-central'}},

    # -p mac --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'branch': 'comm-central'}},

    # -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central'}},

    # -p win64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win64',
              'branch': 'comm-central'}},

    # -p win64 --branch=comm-central --date=2018-03-01
    {'args': {'application': 'thunderbird',
              'platform': 'win64',
              'branch': 'comm-central',
              'date': '2018-03-01'}},

    # -p win32 --branch=comm-central --date=2018-03-01 --build-number=1
    {'args': {'application': 'thunderbird',
              'platform': 'win64',
              'branch': 'comm-central',
              'date': '2018-03-01',
              'build_number': 1}},

    # -p win64 --branch=comm-central --build-id=20180301030201
    {'args': {'application': 'thunderbird',
              'platform': 'win64',
              'branch': 'comm-central',
              'build_id': '20180301030201'}},

    # -p linux --branch=comm-central --build-id=20180301030201 --extension=txt
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central',
              'build_id': '20180301030201',
              'extension': 'txt'}},

    # -p linux --branch=comm-central --build-id=20180301030201 --locale=de
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central',
              'build_id': '20180301030201',
              'locale': 'de'}},
]

tests_tinderbox_scraper = [
    # -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'win32'}},

    # -p win64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'win64'}},

    # -p linux --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'linux'}},

    # -p linux64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'linux64'}},

    # -p mac --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'mac'}},

    # -p win32 --branch=comm-central --debug-build
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'win32',
              'debug_build': True}},

    # -p win32 --branch=comm-central --locale=de
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'win32',
              'locale': 'de'}},

    # -p linux --branch=comm-central --extension=txt
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'linux',
              'extension': 'txt'}},
]


class ThunderbirdRemoteTests(unittest.TestCase):
    """Test all scraper classes for Thunderbird against the remote server"""

    def setUp(self):
        logging.basicConfig(format=' %(levelname)s | %(message)s', level=logging.ERROR)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create a temporary directory for potential downloads
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        mozfile.rmtree(self.temp_dir)

    def test_release_scraper(self):
        for test in tests_release_scraper:
            scraper = mozdownload.ReleaseScraper(destination=self.temp_dir,
                                                 logger=self.logger,
                                                 **test['args'])
            if test.get('url'):
                self.assertEqual(urllib.unquote(scraper.url),
                                 urljoin(BASE_URL, test['url']))

    def test_candidate_scraper(self):
        for test in tests_candidate_scraper:
            scraper = mozdownload.ReleaseCandidateScraper(destination=self.temp_dir,
                                                          logger=self.logger,
                                                          **test['args'])
            if test.get('url'):
                self.assertEqual(urllib.unquote(scraper.url),
                                 urljoin(BASE_URL, test['url']))

    def test_daily_scraper(self):
        for test in tests_daily_scraper:
            mozdownload.DailyScraper(destination=self.temp_dir,
                                     logger=self.logger,
                                     **test['args'])

    def test_tinderbox_scraper(self):
        for test in tests_tinderbox_scraper:
            mozdownload.TinderboxScraper(destination=self.temp_dir,
                                         logger=self.logger,
                                         **test['args'])
