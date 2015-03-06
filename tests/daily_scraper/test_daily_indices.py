#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import DailyScraper
from mozdownload.utils import urljoin
import mozhttpd_base_test as mhttpd

test_params = [
    # -p win32
    {'args': {'platform': 'win32'},
     'build_index': 0,
     'builds': ['2013-10-01-03-02-04-mozilla-central']
     },
    # -p win32 --branch=mozilla-central --build-id=20130706031213
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20130706031213'},
     'build_index': 0,
     'builds': ['2013-07-06-03-12-13-mozilla-central']
     },
    # -p win32 --branch=mozilla-central --date=2013-07-02
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-02'},
     'build_index': 1,
     'builds': ['2013-07-02-03-12-13-mozilla-central', '2013-07-02-04-12-13-mozilla-central']
     },
    # -p win32 --branch=mozilla-central --date=2013-07-02 --build-number=1
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-02',
              'build_number': 1},
     'build_index': 0,
     'builds': ['2013-07-02-03-12-13-mozilla-central', '2013-07-02-04-12-13-mozilla-central']
     }
]


class DailyScraperTest_indices(mhttpd.MozHttpdBaseTest):
    """Test mozdownload daily scraper class"""

    def test_build_indices(self):
        """Testing for correct build_index in DailyScraper"""

        for entry in test_params:
            scraper = DailyScraper(destination=self.temp_dir, base_url=self.wdir,
                                   version=None, log_level='ERROR',
                                   **entry['args'])
            self.assertEqual(scraper.build_index, entry['build_index'])
            self.assertEqual(scraper.builds, entry['builds'])

if __name__ == '__main__':
    unittest.main()
