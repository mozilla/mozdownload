#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import tempfile
import unittest

import mozfile
import mozlog

import mozdownload


tests_daily_scraper = [
    # -p android-api-9 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-api-9',
              'branch': 'mozilla-central'}},

    # Support for API level 11 ended on Jan 28th 2016
    # -p android-api-11 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-api-11',
              'branch': 'mozilla-central',
              'date': '2016-01-28'}},

    # -p android-api-15 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-central'}},

    # -p android-x86 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-x86',
              'branch': 'mozilla-central'}},

    # -p android-api-15 --branch=mozilla-central --date 2016-01-29
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-central',
              'date': '2016-01-29'}},

    # -p android-api-15 --branch=mozilla-central --date 2016-01-29 --build-number=1
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-central',
              'date': '2016-01-29',
              'build_number': 1}},

    # -p android-api-15 --branch=mozilla-central --build-id=20160201030241
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-central',
              'build_id': '20160201030241'}},

    # -p android-api-15 --branch=mozilla-central --build-id=20160201030241 --locale=en-US
    {'args': {'application': 'fennec',
              'locale': 'en-US',
              'platform': 'android-api-15',
              'branch': 'mozilla-central',
              'build_id': '20160201030241'}},

    # -p android-api-15 --branch=mozilla-central --build-id=20160201030241 --extension=txt
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-central',
              'build_id': '20160201030241',
              'extension': 'txt'}},

    # -p android-api-11 --branch=mozilla-aurora --build_id=20160202004008
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-aurora',
              'build_id': '20160202004008'}},
]


class FennecRemoteTests(unittest.TestCase):
    """Test all scraper classes for Fennec against the remote server"""

    def setUp(self):
        self.logger = mozlog.unstructured.getLogger(self.__class__.__name__)
        self.logger.setLevel('ERROR')

        # Create a temporary directory for potential downloads
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        mozfile.rmtree(self.temp_dir)

    def test_daily_scraper(self):
        for test in tests_daily_scraper:
            mozdownload.DailyScraper(destination=self.temp_dir,
                                     logger=self.logger,
                                     **test['args'])


if __name__ == '__main__':
    unittest.main()
