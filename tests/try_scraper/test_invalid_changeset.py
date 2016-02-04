#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

import mozhttpd_base_test as mhttpd

from mozdownload import TryScraper
import mozdownload.errors as errors


tests_with_invalid_changeset = [
    # -a firefox -p win32 --changeset abcd
    {'args': {'application': 'firefox',
              'changeset': 'abcd',
              'platform': 'win32'}},
]

tests = tests_with_invalid_changeset


class TestTryScraperInvalidParameters(mhttpd.MozHttpdBaseTest):
    """test mozdownload TryScraper class with invalid parameters"""

    def test_scraper(self):
        """Testing download scenarios with invalid parameters for TryScraper"""

        for entry in tests:
            self.assertRaises(errors.NotFoundError, TryScraper,
                              destination=self.temp_dir,
                              base_url=self.wdir,
                              logger=self.logger,
                              **entry['args'])


if __name__ == '__main__':
    unittest.main()
