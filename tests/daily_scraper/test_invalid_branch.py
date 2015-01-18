#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import mozlog
import sys
import unittest
import urllib

from mozdownload import DailyScraper, NotFoundError
from mozdownload.utils import urljoin

import mozhttpd_base_test as mhttpd

# testing with an invalid branch parameter should raise an error
tests_with_invalid_branch = [
    # -a firefox -t daily -p win32 --branch=invalid
    {'args': {'application': 'firefox',
              'branch': 'invalid',
              'platform': 'win32'}
     },
    # -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2
    {'args': {'application': 'firefox',
              'branch': 'invalid',
              'platform': 'win32',
              'retry_attempts': 2}
     },
    # -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2 --retry-delay=0
    {'args': {'application': 'firefox',
              'branch': 'invalid',
              'platform': 'win32',
              'retry_attempts': 2,
              'retry_delay': 0.}
     }
]

tests = tests_with_invalid_branch


class TestDailyScraper_invalidBranchParameter(mhttpd.MozHttpdBaseTest):
    """test mozdownload DailyScraper class with invalid branch parameters"""

    def test_scraper(self):
        """Testing download scenarios with invalid branch parameters for DailyScraper"""

        for entry in tests:
            self.assertRaises(NotFoundError, DailyScraper,
                              directory=self.temp_dir,
                              version=None,
                              base_url=self.wdir,
                              log_level='ERROR',
                              **entry['args'])


if __name__ == '__main__':
    unittest.main()
