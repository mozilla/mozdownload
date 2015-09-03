#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import tempfile
import unittest

import mozfile

from mozdownload import DirectScraper
import mozdownload.errors as errors
import mozhttpd_base_test as mhttpd
from mozdownload.utils import urljoin


class TestDirectScraper(mhttpd.MozHttpdBaseTest):
    """test mozdownload direct url scraper"""

    def test_url_download(self):
        filename = 'download_test.txt'
        test_url = urljoin(self.wdir, filename)
        scraper = DirectScraper(url=test_url,
                                destination=self.temp_dir,
                                version=None,
                                log_level='ERROR')
        self.assertEqual(scraper.url, test_url)
        self.assertEqual(scraper.final_url, test_url)
        self.assertEqual(scraper.target,
                         os.path.join(self.temp_dir, filename))

        for attr in ['binary', 'binary_regex', 'path', 'path_regex']:
            self.assertRaises(errors.NotImplementedError, getattr, scraper, attr)

        scraper.download()
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir,
                                                    scraper.target)))


if __name__ == '__main__':
    unittest.main()
