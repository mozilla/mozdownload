#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import TryScraper
from mozdownload.utils import urljoin
import mozhttpd_base_test as mhttpd

firefox_tests = [
    # -p mac64 --changeset=8fcac92cfcad
    {'args': {'platform': 'mac64',
              'changeset': '8fcac92cfcad'},
     'filename': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
     'url': 'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
            'try-macosx64/firefox-38.0a1.en-US.mac.dmg'},
    # -p mac --changeset=8fcac92cfcad
    {'args': {'platform': 'mac',
              'changeset': '8fcac92cfcad'},
     'filename': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
     'url': 'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
            'try-macosx64/firefox-38.0a1.en-US.mac.dmg'},
    # -a firefox -p linux64 --changeset=8fcac92cfcad
    {'args': {'platform': 'linux64',
              'changeset': '8fcac92cfcad'},
     'filename': '8fcac92cfcad-firefox-38.0a1.en-US.linux-x86_64.tar.bz2',
     'url': 'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
            'try-linux64/firefox-38.0a1.en-US.linux-x86_64.tar.bz2'},
    # -a firefox -p linux --debug-build
    {'args': {'platform': 'linux',
              'changeset': '8fcac92cfcad',
              'debug_build': True},
     'filename': '8fcac92cfcad-debug-firefox-38.0a1.en-US.linux-i686.tar.bz2',
     'url': 'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
            'try-linux-debug/firefox-38.0a1.en-US.linux-i686.tar.bz2'},
    # -a firefox -p win32 --changeset=8fcac92cfcad
    {'args': {'platform': 'win32',
              'changeset': '8fcac92cfcad'},
     'filename': '8fcac92cfcad-firefox-38.0a1.en-US.win32.installer.exe',
     'url': 'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
            'try-win32/firefox-38.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win64 --changeset=8fcac92cfcad
    {'args': {'platform': 'win64',
              'changeset': '8fcac92cfcad'},
     'filename': '8fcac92cfcad-firefox-38.0a1.en-US.win64.installer.exe',
     'url': 'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
            'try-win64/firefox-38.0a1.en-US.win64.installer.exe'},
]

tests = firefox_tests


class TryScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload TryScraper class"""

    def test_scraper(self):
        """Testing various download scenarios for TryScraper"""

        for entry in tests:
            scraper = TryScraper(destination=self.temp_dir,
                                 base_url=self.wdir,
                                 log_level='ERROR',
                                 **entry['args'])
            expected_filename = os.path.join(self.temp_dir, entry['filename'])
            self.assertEqual(scraper.filename, expected_filename)
            self.assertEqual(urllib.unquote(scraper.url),
                             urljoin(self.wdir, entry['url']))

if __name__ == '__main__':
    unittest.main()
