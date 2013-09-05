#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# TODO:
# Tests of base class:
# - detect_platform
# - show_matching_builds

# - TimeoutError needs revisiting. facilitate HTTP response delay... somehow

import os
import unittest

import mozhttpd
import requests

from mozdownload import *
from mozdownload.utils import create_md5

import mozhttpd_template_test as mhttpd


class BaseScraperTest(mhttpd.MozHttpdTest):
    """Testing the basic functionality of the Base Scraper Class"""

    def test_platform_regex(self):
        """Test for correct platform_regex output"""

        # Copy of PLATFORM_FRAGMENTS
        platform_dict = {'linux': 'linux-i686',
                         'linux64': 'linux-x86_64',
                         'mac': 'mac',
                         'mac64': 'mac64',
                         'win32': 'win32',
                         'win64': 'win64-x86_64'}

        for key in platform_dict:
            scraper = Scraper(directory=self.temp_dir,
                              version=None,
                              platform=key)
            self.assertEqual(scraper.platform_regex, platform_dict[key])

    def test_download(self):
        """Test download method"""

        filename = 'download_test.txt'
        # standard download
        test_url = urljoin(self.wdir, 'download_test.txt')
        scraper = DirectScraper(url=test_url,
                                directory=self.temp_dir,
                                version=None)
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    filename)))
        # Compare original and downloaded file via md5 hash
        original = create_md5(os.path.join(mhttpd.HERE, mhttpd.WDIR, filename))
        down = create_md5(os.path.join(self.temp_dir, filename))
        self.assertEqual(original, down)

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
        test_url2 = urljoin(self.wdir, 'does_not_exist.html')
        scraper2 = DirectScraper(url=test_url2,
                                 directory=self.temp_dir,
                                 version=None)
        self.assertRaises(requests.exceptions.RequestException, scraper2.download)

    def test_notimplementedexceptions(self):
        scraper = Scraper(directory=self.temp_dir,
                          version=None)
        for attr in ['binary', 'binary_regex', 'path_regex']:
            self.assertRaises(NotImplementedError, getattr, scraper, attr)
        self.assertRaises(NotImplementedError, scraper.build_filename, 'invalid binary')

if __name__ == '__main__':
    unittest.main()
