#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from mozdownload import DailyScraper
import mozdownload.errors as errors

import mozhttpd_base_test as mhttpd


# testing with an invalid branch parameter should raise an error
tests_with_invalid_branch = [
    # -a firefox -t daily -p win32 --branch=invalid
    {'args': {'application': 'firefox',
              'branch': 'invalid',
              'platform': 'win32'}
     }
]

tests = tests_with_invalid_branch


class TestDailyScraperInvalidBranch(mhttpd.MozHttpdBaseTest):
    """test mozdownload DailyScraper class with invalid branch parameters"""

    def test_invalid_branch(self):
        """Testing download scenarios with invalid branch parameters for DailyScraper"""

        for entry in tests:
            self.assertRaises(errors.NotFoundError, DailyScraper,
                              destination=self.temp_dir,
                              base_url=self.wdir,
                              logger=self.logger,
                              **entry['args'])


if __name__ == '__main__':
    unittest.main()
