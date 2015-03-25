#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import ReleaseCandidateScraper
from mozdownload.utils import urljoin
import mozhttpd_base_test as mhttpd

test_params = [
    # -a firefox -p win32 -v 21.0 --build-number=1
    {'args': {'build_number': '1',
              'platform': 'win32',
              'version': '21.0'},
    'build_index': 0,
    'build_number': '1',
    'builds': ['build1']
     },
    # -a firefox -p mac -v 21.0 --build-number=3
    {'args': {'build_number': '3',
              'platform': 'mac',
              'version': '21.0'},
    'build_index': 0,
    'build_number': '3',
    'builds': ['build3']
     },
    # -a firefox -p linux -v 21.0 --build-number=2
    # Invalid build-number
    {'args': {'build_number': '2',
              'platform': 'linux',
              'version': '21.0'},
    # build_index = len(parser.entries) - 1
    'build_index': 1,
    'build_number': '2',
    'builds': ['build1', 'build3']
     }
]


class ReleaseCandidateScraperTest_build_indices(mhttpd.MozHttpdBaseTest):
    """test indices in mozdownload scraper class"""

    def test_build_indices(self):
        """Testing indices in choosing builds for ReleaseCandidateScraper"""

        for entry in test_params:
            scraper = ReleaseCandidateScraper(destination=self.temp_dir,
                                              base_url=self.wdir,
                                              log_level='ERROR',
                                              **entry['args'])
            self.assertEqual(scraper.build_index, entry['build_index'])
            self.assertEqual(scraper.build_number, entry['build_number'])
            self.assertEqual(scraper.builds, entry['builds'])

if __name__ == '__main__':
    unittest.main()
