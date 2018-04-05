#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from mozdownload.parser import DirectoryParser
from mozdownload.utils import urljoin

import mozhttpd_base_test as mhttpd


class DirectoryParserTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_init(self):
        """Testing the basic functionality of the DirectoryParser Class"""

        # DirectoryParser returns output
        parser = DirectoryParser(self.wdir)

        # relies on the presence of other files in the directory
        # Checks if DirectoryParser lists the server entries
        self.assertNotEqual(parser.entries, [], "parser.entries were not listed")

        # path_regex to mozdownload -t release -p win32 -v latest
        testpath = urljoin(self.wdir, 'directoryparser/')
        parser1 = DirectoryParser(testpath)
        parser1.entries.sort()
        testdir = os.listdir(urljoin(mhttpd.HERE, 'data', 'directoryparser'))
        testdir.sort()
        self.assertEqual(parser1.entries, testdir)

    def test_filter(self):
        """Testing the DirectoryParser filter method"""
        parser = DirectoryParser(urljoin(self.wdir, 'directoryparser', 'filter/'))

        # Get the contents of the folder - dirs and files
        folder_path = urljoin(mhttpd.HERE, mhttpd.WDIR, 'directoryparser',
                              'filter')
        contents = os.listdir(folder_path)
        contents.sort()
        self.assertEqual(parser.entries, contents)

        # filter out files
        parser.entries = parser.filter(r'^\d+$')

        # Get only the subdirectories of the folder
        dirs = os.walk(folder_path).next()[1]
        dirs.sort()
        self.assertEqual(parser.entries, dirs)

        # Test filter method with a function
        parser.entries = parser.filter(lambda x: x == dirs[0])
        self.assertEqual(parser.entries, [dirs[0]])

    def test_names_with_spaces(self):
        parser = DirectoryParser(urljoin(self.wdir, 'directoryparser', 'some spaces/'))

        # Get the contents of the folder - dirs and files
        folder_path = urljoin(mhttpd.HERE, mhttpd.WDIR, 'directoryparser',
                              'some spaces')
        contents = os.listdir(folder_path)
        contents.sort()
        self.assertEqual(parser.entries, contents)
