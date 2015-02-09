#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

import requests

import mozdownload
from mozdownload.utils import create_md5, urljoin
import mozhttpd_base_test as mhttpd


class BaseScraperTest(mhttpd.MozHttpdBaseTest):
    """Testing the basic functionality of the Base Scraper Class"""

    def test_platform_regex(self):
        """Test for correct platform_regex output"""

        for key in mozdownload.PLATFORM_FRAGMENTS:
            scraper = mozdownload.Scraper(directory=self.temp_dir,
                                          version=None,
                                          platform=key)
            self.assertEqual(scraper.platform_regex,
                             mozdownload.PLATFORM_FRAGMENTS[key])

    def test_download(self):
        """Test download method"""

        filename = 'download_test.txt'
        # standard download
        test_url = urljoin(self.wdir, 'download_test.txt')
        scraper = mozdownload.DirectScraper(url=test_url,
                                            directory=self.temp_dir,
                                            version=None,
                                            log_level='ERROR')
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    filename)))
        # Compare original and downloaded file via md5 hash
        md5_original = create_md5(os.path.join(mhttpd.HERE,
                                               mhttpd.WDIR,
                                               filename))
        md5_downloaded = create_md5(os.path.join(self.temp_dir, filename))
        self.assertEqual(md5_original, md5_downloaded)

        # RequestException
        test_url1 = urljoin(self.wdir, 'does_not_exist.html')
        scraper1 = mozdownload.DirectScraper(url=test_url1,
                                             directory=self.temp_dir,
                                             version=None,
                                             log_level='ERROR')
        self.assertRaises(requests.exceptions.RequestException,
                          scraper1.download)

        # Covering retry_attempts
        test_url2 = urljoin(self.wdir, 'does_not_exist.html')
        scraper2 = mozdownload.DirectScraper(url=test_url2,
                                             directory=self.temp_dir,
                                             version=None,
                                             retry_attempts=3,
                                             retry_delay=1.0,
                                             log_level='ERROR')
        self.assertRaises(requests.exceptions.RequestException,
                          scraper2.download)

    def test_notimplementedexceptions(self):
        scraper = mozdownload.Scraper(directory=self.temp_dir,
                                      version=None, log_level='ERROR')
        for attr in ['binary', 'binary_regex', 'path_regex']:
            self.assertRaises(mozdownload.NotImplementedError, getattr,
                              scraper, attr)
        self.assertRaises(mozdownload.NotImplementedError,
                          scraper.build_filename, 'invalid binary')

    def test_authentication(self):
        """testing with basic authentication"""
        username = 'mozilla'
        password = 'mozilla'
        basic_auth_url = 'http://mozqa.com/data/mozqa.com/http_auth/basic/'

        # test with invalid authentication
        scraper = mozdownload.DirectScraper(directory=self.temp_dir,
                                            url=basic_auth_url,
                                            version=None)
        self.assertRaises(requests.exceptions.HTTPError, scraper.download)

        # testing with valid authentication
        scraper = mozdownload.DirectScraper(directory=self.temp_dir,
                                            url=basic_auth_url,
                                            version=None,
                                            username=username,
                                            password=password)
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    'mozqa.com')))

    def test_optional_authenticaiton(self):
        """testing with optional basic authentication"""
        optional_auth_url = 'https://ci.mozilla.org/'

        # requires optional authentication with no data specified
        scraper = mozdownload.DirectScraper(directory=self.temp_dir,
                                            url=optional_auth_url,
                                            version=None)
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    'ci.mozilla.org')))

if __name__ == '__main__':
    unittest.main()
