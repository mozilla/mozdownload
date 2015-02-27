#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import mozlog
import unittest

from mozdownload import DailyScraper, NotFoundError
from mozdownload.utils import urljoin

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


class TestDailyScraper(mhttpd.MozHttpdBaseTest):
    """test mozdownload DailyScraper class with invalid branch parameters"""

    def test_invalid_branch(self):
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
