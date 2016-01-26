#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from mock import patch

from mozdownload import TinderboxScraper, errors
import mozhttpd_base_test as mhttpd


class TestTinderboxScraperRevision(mhttpd.MozHttpdBaseTest):
    """Test mozdownload tinderbox scraper class for revision argument."""

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_valid_revision(self, query_builds_by_revision):
        build_path = self.wdir + '/firefox/tinderbox-builds/mozilla-central-linux/1374583608/'
        query_builds_by_revision.return_value = [build_path]

        scraper = TinderboxScraper(destination=self.temp_dir,
                                   base_url=self.wdir,
                                   logger=self.logger,
                                   platform='linux',
                                   revision='6b92cb377496')
        self.assertEqual(len(scraper.builds), 1)
        self.assertEqual(scraper.url, build_path + 'firefox-25.0a1.en-US.linux-i686.tar.bz2')

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_invalid_revision(self, query_builds_by_revision):
        query_builds_by_revision.return_value = []

        with self.assertRaises(errors.NotFoundError):
            TinderboxScraper(destination=self.temp_dir,
                             base_url=self.wdir,
                             logger=self.logger,
                             platform='linux',
                             revision='not_valid')


if __name__ == '__main__':
    unittest.main()
