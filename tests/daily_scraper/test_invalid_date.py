#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import mozlog
import sys
import unittest
import urllib

from mozdownload import DailyScraper
from mozdownload.utils import urljoin

import mozhttpd_base_test as mhttpd


# testing with an invalid date parameter should raise an error
tests_with_invalid_date = [
    # -p win32 --branch=mozilla-central --date=20140317030202
    {'args': {'branch': 'mozilla-central',
              'date': '20140317030202',
              'locale': 'pt-PT',
              'platform': 'win32'}
    },
    # -p win64 --branch=mozilla-central --date=2013/07/02
     {'args': {'branch': 'mozilla-central',
              'date': '2013/07/02',
              'platform': 'win64'},
     },
    # -p win32 --branch=mozilla-central --date=2013-March-15
    {'args': {'branch': 'mozilla-central',
              'date': '2013-March-15',
              'platform': 'win32'},
    }
]

tests = tests_with_invalid_date


class TestDailyScraper_invalidParameters(mhttpd.MozHttpdBaseTest):
    """test mozdownload DailyScraper class with invalid parameters"""

    def test_scraper(self):
        """Testing download scenarios with invalid parameters for DailyScraper"""

        for entry in tests:
            self.assertRaises(ValueError, DailyScraper,
                              destination=self.temp_dir,
                              version=None,
                              base_url=self.wdir,
                              log_level='ERROR',
                              **entry['args'])


if __name__ == '__main__':
    unittest.main()
