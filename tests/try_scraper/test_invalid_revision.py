#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from mock import patch

from mozdownload import TryScraper
import mozdownload.errors as errors
import mozhttpd_base_test as mhttpd


class TestTryScraperInvalidParameters(mhttpd.MozHttpdBaseTest):
    """test mozdownload TryScraper class with invalid parameters"""

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_scraper(self, query_builds_by_revision):
        """Testing download scenarios with invalid parameters for TryScraper"""
        query_builds_by_revision.return_value = []

        with self.assertRaises(errors.NotFoundError):
            TryScraper(destination=self.temp_dir,
                       base_url=self.wdir,
                       logger=self.logger,
                       platform='win32',
                       revision='abc'
                       )


if __name__ == '__main__':
    unittest.main()
