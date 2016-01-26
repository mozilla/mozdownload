#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from mock import patch
from mozdownload import DailyScraper, errors
import mozhttpd_base_test as mhttpd


class TestDailyScraperRevision(mhttpd.MozHttpdBaseTest):
    """Test mozdownload daily scraper class for revision argument."""

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_valid_revision(self, query_builds_by_revision):
        build_path = self.wdir + '/firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/'
        query_builds_by_revision.return_value = [build_path]

        scraper = DailyScraper(destination=self.temp_dir,
                               base_url=self.wdir,
                               logger=self.logger,
                               platform='linux',
                               revision='6b92cb377496')
        self.assertEqual(len(scraper.builds), 1)
        self.assertEqual(scraper.url, build_path + 'firefox-27.0a1.en-US.linux-i686.tar.bz2')

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_invalid_revision(self, query_builds_by_revision):
        query_builds_by_revision.return_value = []

        with self.assertRaises(errors.NotFoundError):
            DailyScraper(destination=self.temp_dir,
                         base_url=self.wdir,
                         logger=self.logger,
                         platform='linux',
                         revision='not_valid')


if __name__ == '__main__':
    unittest.main()
