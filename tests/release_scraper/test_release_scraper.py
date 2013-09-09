#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

import mozhttpd

from mozdownload import ReleaseScraper

import mozhttpd_template_test as mhttpd


class ReleaseScraperTest(mhttpd.MozHttpdTest):
    """test mozdownload scraper class"""

    def test_latest_version(self):
        """Testing the basic functionality of the ReleaseScraper Class"""
        scraper = ReleaseScraper(directory=self.temp_dir,
                                 version='latest',
                                 platform='win32',
                                 base_url=self.wdir)

        target_cmp = os.path.join(self.temp_dir,
                                  'firefox-latest.en-US.win32.exe')
        self.assertEqual(scraper.target, target_cmp)

if __name__ == '__main__':
    unittest.main()
