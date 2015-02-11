#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from mozdownload import TryScraper
from mozdownload import NotFoundError

import mozhttpd_base_test as mhttpd


tests_with_invalid_changeset = [
    # -a firefox -p win32 --changeset abcd
    {'args': {'application': 'firefox',
              'changeset': 'abcd',
              'platform': 'win32'}
    },
]

tests = tests_with_invalid_changeset


class TestTryScraper_invalidParameters(mhttpd.MozHttpdBaseTest):
    """test mozdownload TryScraper class with invalid parameters"""

    def test_scraper(self):
        """Testing download scenarios with invalid parameters for TryScraper"""

        for entry in tests:
            self.assertRaises(NotFoundError, TryScraper,
                              directory=self.temp_dir,
                              version=None,
                              base_url=self.wdir,
                              log_level='ERROR',
                              **entry['args'])


if __name__ == '__main__':
    unittest.main()
