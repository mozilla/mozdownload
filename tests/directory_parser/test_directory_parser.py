#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import unittest

import mozhttpd

from mozdownload import DirectoryParser

sys.path.insert(0, os.path.abspath(".."))
import mozhttpd_template_test as mhttpd


class DirectoryParserTest(mhttpd.MozHttpdTest):
    """test mozdownload scraper class"""

    def test_parser(self):
        """Testing the basic functionality of the DirectoryParser Class"""
        server_address = "http://%s:%s" % (self.httpd.host, self.httpd.port)
        parser = DirectoryParser(server_address)

        # relies on the presence of other files in the directory
        # Checks if DirectoryParser lists the server entries
        self.assertNotEqual(parser.entries, [], "parser.entries were not listed")

if __name__ == '__main__':
    unittest.main()
