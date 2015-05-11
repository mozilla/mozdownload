#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

import mozfile
import mozhttpd_base_test as mhttpd
from mozprocess import processhandler

tests = [
    # ReleaseScraper
    {'command': ['-v', 'latest'],
     'fname': 'firefox-latest.en-US.linux64.tar.bz2'},

    # ReleaseCandidateScraper
    {'command': ['-t', 'candidate', '-v', '21.0', '-p', 'win32',],
     'fname': 'firefox-21.0-build3.en-US.win32.exe'},

    # DailyScraper
    {'command': ['-t', 'daily', '-p', 'win32'],
     'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe'},

    # TinderboxScraper
    {'command': ['-t', 'tinderbox', '-p', 'win32'],
     'fname': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},

    # TryScraper
    {'command': ['-t', 'try', '-p', 'mac64', '--changeset=8fcac92cfcad'],
     'fname': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg'},
]


class CorrectScraperTest(mhttpd.MozHttpdBaseTest):
    """Test mozdownload for correct choice of scraper"""

    def test_scraper(self):
        """Testing various download scenarios for DailyScraper"""

        for entry in tests:
            command = ['./mozdownload/scraper.py',
                        '--base_url=%s' % self.wdir,
                        '--destination=%s' % self.temp_dir]
            p = processhandler.ProcessHandler(command + entry['command'])
            p.run()
            p.wait()
            dir_content = os.listdir(self.temp_dir)
            self.assertTrue(entry['fname'] in dir_content)

            mozfile.remove(os.path.join(self.temp_dir, entry['fname']))

if __name__ == '__main__':
    unittest.main()
