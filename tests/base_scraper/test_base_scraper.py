#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# TODO:
# Tests of base class:
# - detect_platform
# - show_matching_builds

import os
import unittest

import mozhttpd
import requests

from mozdownload import DirectScraper, NotFoundError, NotImplementedError, Scraper, TimeoutError

import mozhttpd_template_test as mhttpd


class BaseScraperTest(mhttpd.MozHttpdTest):
    """Testing the basic functionality of the Base Scraper Class"""

    def test_platform_regex(self):
        """Test for correct platform_regex output"""
        scraper = Scraper(directory=self.temp_dir,
                          version=None,
                          platform="win32")
        self.assertEqual(scraper.platform_regex, 'win32')

        scraper1 = Scraper(directory=self.temp_dir,
                           version=None,
                           platform="win64")
        self.assertEqual(scraper1.platform_regex, 'win64-x86_64')

        scraper2 = Scraper(directory=self.temp_dir,
                           version=None,
                           platform="linux")
        self.assertEqual(scraper2.platform_regex, 'linux-i686')

        scraper3 = Scraper(directory=self.temp_dir,
                           version=None,
                           platform="linux64")
        self.assertEqual(scraper3.platform_regex, 'linux-x86_64')

        scraper4 = Scraper(directory=self.temp_dir,
                           version=None,
                           platform="mac")
        self.assertEqual(scraper4.platform_regex, 'mac')

        scraper5 = Scraper(directory=self.temp_dir,
                           version=None,
                           platform="mac64")
        self.assertEqual(scraper5.platform_regex, 'mac64')

    def test_download(self):
        """Test download method"""

        # standard download
        test_url = 'https://mozqa.com/index.html'
        scraper = DirectScraper(url=test_url,
                                directory=self.temp_dir,
                                version=None)
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    scraper.target)))

        # TimeoutError
        test_url1 = 'http://www.mozilla.org/media/img/firefox/fx/android-phone-tablet.jpg'
        scraper1 = DirectScraper(url=test_url1,
                                 directory=self.temp_dir,
                                 version=None,
                                 timeout=0.1,
                                 retry_attempts=2,
                                 retry_delay=0.1)
        self.assertRaises(TimeoutError, scraper1.download)

        # RequestException
        test_url2 = 'https://mozqa.com/wrong_index.html'
        scraper2 = DirectScraper(url=test_url2,
                                 directory=self.temp_dir,
                                 version=None)
        self.assertRaises(requests.exceptions.RequestException, scraper2.download)

    def test_exceptions(self):
        scraper = Scraper(directory=self.temp_dir,
                          version=None)
        for attr in ['binary', 'binary_regex', 'path_regex']:
            self.assertRaises(NotImplementedError, getattr, scraper, attr)
        self.assertRaises(NotImplementedError, scraper.build_filename, 'invalid binary')

if __name__ == '__main__':
    unittest.main()
