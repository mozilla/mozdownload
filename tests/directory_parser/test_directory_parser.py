#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

import mozhttpd

from mozdownload import DirectoryParser, ReleaseScraper, TinderboxScraper
from mozdownload.utils import urljoin

import mozhttpd_template_test as mhttpd


class DirectoryParserTest(mhttpd.MozHttpdTest):
    """test mozdownload scraper class"""

    def test_init(self):
        """Testing the basic functionality of the DirectoryParser Class"""

        # DirectoryParser returns output
        parser = DirectoryParser(self.server_address)

        # relies on the presence of other files in the directory
        # Checks if DirectoryParser lists the server entries
        self.assertNotEqual(parser.entries, [], "parser.entries were not listed")

        # DirectoryParser returns correct filename
        scraper = ReleaseScraper(directory=self.temp_dir,
                                 version='latest',
                                 platform='win32',
                                 base_url=self.wdir)
        parser1 = DirectoryParser(scraper.path)
        self.assertEqual(parser1.entries[0], 'firefox-latest.en-US.win32.exe')

    def test_filter(self):
        """Testing the DirectoryParser filter method"""
        scraper = TinderboxScraper(directory=self.temp_dir,
                                   version=None,
                                   platform='win32',
                                   base_url=self.wdir)
        parser = DirectoryParser(urljoin(scraper.base_url,
                                         scraper.build_list_regex))

        # Get the contents of the folder
        folder_path = urljoin(mhttpd.HERE, mhttpd.WDIR, 'firefox',
                              'tinderbox-builds', 'mozilla-central-win32')
        contents = os.listdir(folder_path)
        contents.sort()
        self.assertEqual(parser.entries, contents)

        # filter out files
        parser.entries = parser.filter(r'^\d+$')

        # Get only the subdirectories of the folder
        dirs = os.walk(folder_path).next()[1]
        dirs.sort()
        self.assertEqual(parser.entries, dirs)


if __name__ == '__main__':
    unittest.main()
