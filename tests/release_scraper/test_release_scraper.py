#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import unittest

import mozhttpd

from mozdownload import ReleaseScraper

sys.path.insert(0, os.path.abspath(".."))
import mozhttpd_template_test as mhttpd


class ReleaseScraperTest(mhttpd.MozHttpdTest):
    """test mozdownload scraper class"""

    def test_version_latest(self):
        """Testing the basic functionality of the ReleaseScraper Class"""
        server_address = "http://%s:%s" % (self.httpd.host, self.httpd.port)
        wdir = '/'.join([server_address, mhttpd.WDIR])
        scraper = ReleaseScraper(os.getcwd(), 'latest', platform='win32',
                                 base_url=wdir)
        scraper.download()
        self.assertEqual(scraper.target, os.path.join(os.getcwd(), os.path.basename(scraper.target)))
        os.remove(os.path.join(os.getcwd(), os.path.basename(scraper.target)))

if __name__ == '__main__':
    unittest.main()
