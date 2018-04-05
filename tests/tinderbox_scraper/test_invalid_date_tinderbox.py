#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from mozdownload import TinderboxScraper

import mozhttpd_base_test as mhttpd


# testing with an invalid date parameter should download the latest build for
# localized builds
tests_with_invalid_date = [
    # -a firefox -p win32 --branch=mozilla-central --date=20140317030202
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'date': '20140317030202',
              'locale': 'pt-PT',
              'platform': 'win32'}},
    # -p win32 --branch=mozilla-central  --date=invalid
    {'args': {'branch': 'mozilla-central',
              'date': 'invalid',
              'locale': 'pt-PT',
              'platform': 'win32'}},
    # -p win64 --branch=mozilla-central --date=2013/07/02
    {'args': {'branch': 'mozilla-central',
              'date': '2013/07/02',
              'platform': 'win64'}},
    # -p win32 --branch=mozilla-central --date=2013-March-15
    {'args': {'branch': 'mozilla-central',
              'date': '2013-March-15',
              'platform': 'win32'}}
]

tests = tests_with_invalid_date


class TestTinderboxScraperInvalidParameters(mhttpd.MozHttpdBaseTest):
    """test mozdownload TinderboxScraper class with invalid parameters"""

    def test_scraper(self):
        """Testing download scenarios with invalid parameters for TinderboxScraper"""

        for entry in tests:
            self.assertRaises(ValueError, TinderboxScraper,
                              destination=self.temp_dir,
                              base_url=self.wdir,
                              logger=self.logger,
                              **entry['args'])
