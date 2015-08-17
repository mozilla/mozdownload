#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

import mozhttpd_base_test as mhttpd
import requests

import mozdownload
import mozdownload.errors as errors
from mozdownload.scraper import PLATFORM_FRAGMENTS
from mozdownload.utils import create_md5, urljoin


class TestBaseScraper(mhttpd.MozHttpdBaseTest):
    """Testing the basic functionality of the Base Scraper Class"""

    def test_platform_regex(self):
        """Test for correct platform_regex output"""

        for key in PLATFORM_FRAGMENTS:
            scraper = mozdownload.Scraper(destination=self.temp_dir,
                                          version=None,
                                          platform=key)
            self.assertEqual(scraper.platform_regex,
                             PLATFORM_FRAGMENTS[key])

    def test_download(self):
        """Test download method"""

        filename = 'download_test.txt'
        # standard download
        test_url = urljoin(self.wdir, filename)
        scraper = mozdownload.DirectScraper(url=test_url,
                                            destination=self.temp_dir,
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
                                             destination=self.temp_dir,
                                             version=None,
                                             log_level='ERROR')
        self.assertRaises(requests.exceptions.RequestException,
                          scraper1.download)

        # Covering retry_attempts
        test_url2 = urljoin(self.wdir, 'does_not_exist.html')
        scraper2 = mozdownload.DirectScraper(url=test_url2,
                                             destination=self.temp_dir,
                                             version=None,
                                             retry_attempts=3,
                                             retry_delay=1.0,
                                             log_level='ERROR')
        self.assertRaises(requests.exceptions.RequestException,
                          scraper2.download)

    def test_notimplementedexceptions(self):
        scraper = mozdownload.Scraper(destination=self.temp_dir,
                                      version=None, log_level='ERROR')
        for attr in ['binary', 'binary_regex', 'path_regex']:
            self.assertRaises(errors.NotImplementedError, getattr,
                              scraper, attr)
        self.assertRaises(errors.NotImplementedError,
                          scraper.build_filename, 'invalid binary')

    def test_authentication(self):
        """testing with basic authentication"""
        username = 'mozilla'
        password = 'mozilla'
        basic_auth_url = 'http://mozqa.com/data/mozqa.com/http_auth/basic/'

        # test with invalid authentication
        scraper = mozdownload.DirectScraper(destination=self.temp_dir,
                                            url=basic_auth_url,
                                            version=None,
                                            log_level='ERROR')
        self.assertRaises(requests.exceptions.HTTPError, scraper.download)

        # testing with valid authentication
        scraper = mozdownload.DirectScraper(destination=self.temp_dir,
                                            url=basic_auth_url,
                                            version=None,
                                            log_level='ERROR',
                                            username=username,
                                            password=password)
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    'mozqa.com')))

    def test_optional_authentication(self):
        """testing with optional basic authentication"""
        optional_auth_url = 'https://ci.mozilla.org/'

        # requires optional authentication with no data specified
        scraper = mozdownload.DirectScraper(destination=self.temp_dir,
                                            url=optional_auth_url,
                                            version=None,
                                            log_level='ERROR')
        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    'ci.mozilla.org')))

    def test_destination(self):
        """Test for various destination scenarios"""

        filename = 'download_test.txt'
        test_url = urljoin(self.wdir, filename)

        # destination is directory
        scraper = mozdownload.DirectScraper(url=test_url,
                                            destination=self.temp_dir,
                                            version=None,
                                            log_level='ERROR')
        self.assertEqual(scraper.target, os.path.join(self.temp_dir, filename))

        # destination has directory path with filename
        destination = os.path.join(self.temp_dir, filename)
        scraper = mozdownload.DirectScraper(url=test_url,
                                            destination=destination,
                                            version=None,
                                            log_level='ERROR')
        self.assertEqual(scraper.target, destination)

        # destination only has filename
        scraper = mozdownload.DirectScraper(url=test_url,
                                            destination=filename,
                                            version=None,
                                            log_level='ERROR')
        self.assertEqual(scraper.target, os.path.abspath(filename))

        # destination directory does not exist
        destination = os.path.join(self.temp_dir, 'temp_folder', filename)
        scraper = mozdownload.DirectScraper(url=test_url,
                                            destination=destination,
                                            version=None,
                                            log_level='ERROR')
        self.assertEqual(scraper.destination, destination)

        # ensure that multiple non existing directories are created
        destination = os.path.join(self.temp_dir, 'tmp1', 'tmp2', filename)
        scraper = mozdownload.DirectScraper(url=test_url,
                                            destination=destination,
                                            version=None,
                                            log_level='ERROR')
        self.assertEqual(scraper.destination, destination)


if __name__ == '__main__':
    unittest.main()
