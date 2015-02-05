#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import tempfile
import unittest

import mozfile

from mozdownload import DirectScraper, NotImplementedError, urljoin
import mozhttpd_base_test as mhttpd



class TestDirectScraper(mhttpd.MozHttpdBaseTest):
    """test mozdownload direct url scraper"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        mozfile.rmtree(self.temp_dir)

    def test_url_download(self):
        test_url = urljoin(self.wdir, 'download_test.txt')
        scraper = DirectScraper(url=test_url,
                                directory=self.temp_dir,
                                version=None,
                                log_level='ERROR')
        self.assertEqual(scraper.url, test_url)
        self.assertEqual(scraper.final_url, test_url)
        self.assertEqual(scraper.target,
                         os.path.join(self.temp_dir, 'index.html'))

        for attr in ['binary', 'binary_regex', 'path', 'path_regex']:
            self.assertRaises(NotImplementedError, getattr, scraper, attr)

        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    scraper.target)))


if __name__ == '__main__':
    unittest.main()
