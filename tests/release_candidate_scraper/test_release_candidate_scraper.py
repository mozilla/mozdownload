#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import ReleaseCandidateScraper
from mozdownload.utils import urljoin

import mozhttpd_base_test as mhttpd


firefox_tests = [
    # -a firefox -p linux -v 23.0.1
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.en-US.linux.tar.bz2',
     'url': 'firefox/candidates/23.0.1-candidates/build3/linux-i686/en-US/firefox-23.0.1.tar.bz2'},
    # -a firefox -p linux64 -v 23.0.1
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.en-US.linux64.tar.bz2',
     'url': 'firefox/candidates/23.0.1-candidates/build3/linux-x86_64/en-US/firefox-23.0.1.tar.bz2'},
    # -a firefox -p mac -v 23.0.1
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.en-US.mac.dmg',
     'url': 'firefox/candidates/23.0.1-candidates/build3/mac/en-US/Firefox 23.0.1.dmg'},
    # -a firefox -p win32 -v 23.0.1
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.en-US.win32.exe',
     'url': 'firefox/candidates/23.0.1-candidates/build3/win32/en-US/Firefox Setup 23.0.1.exe'},
    # -p win64 -v 23.0.1
    {'args': {'platform': 'win64',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.en-US.win64.exe',
     'url': 'firefox/candidates/23.0.1-candidates/build3/win64/en-US/Firefox Setup 23.0.1.exe'},
    # -a firefox -p win32 -v 23.0.1 -l de
    {'args': {'application': 'firefox',
              'locale': 'de',
              'platform': 'win32',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.de.win32.exe',
     'url': 'firefox/candidates/23.0.1-candidates/build3/win32/de/Firefox Setup 23.0.1.exe'},
    # -a firefox -p win32 -v 23.0.1 --build-number=1
    {'args': {'application': 'firefox',
              'build_number': '1',
              'platform': 'win32',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build1.en-US.win32.exe',
     'url': 'firefox/candidates/23.0.1-candidates/build1/win32/en-US/Firefox Setup 23.0.1.exe'},
    # -a firefox -p win32 -v 23.0.1 --stub
    {'args': {'application': 'firefox',
              'is_stub_installer': True,
              'platform': 'win32',
              'version': '23.0.1'},
     'filename': 'firefox-23.0.1-build3.en-US.win32-stub.exe',
     'url': 'firefox/candidates/23.0.1-candidates/build3/win32/en-US/Firefox Setup Stub 23.0.1.exe'},
]

thunderbird_tests = [
    # -a thunderbird -p linux -v 17.0
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': '17.0'},
     'filename': 'thunderbird-17.0-build3.en-US.linux.tar.bz2',
     'url': 'thunderbird/candidates/17.0-candidates/build3/linux-i686/en-US/thunderbird-17.0.tar.bz2'},
    # -a thunderbird -p linux64 -v 17.0
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': '17.0'},
     'filename': 'thunderbird-17.0-build3.en-US.linux64.tar.bz2',
     'url': 'thunderbird/candidates/17.0-candidates/build3/linux-x86_64/en-US/thunderbird-17.0.tar.bz2'},
    # -a thunderbird -p mac -v 17.0
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': '17.0'},
     'filename': 'thunderbird-17.0-build3.en-US.mac.dmg',
     'url': 'thunderbird/candidates/17.0-candidates/build3/mac/en-US/Thunderbird 17.0.dmg'},
    # -a thunderbird -p win32 -v 17.0
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '17.0'},
     'filename': 'thunderbird-17.0-build3.en-US.win32.exe',
     'url': 'thunderbird/candidates/17.0-candidates/build3/win32/en-US/Thunderbird Setup 17.0.exe'},
    # -a thunderbird -p win32 -v 17.0 -l de
    {'args': {'application': 'thunderbird',
              'locale': 'de',
              'platform': 'win32',
              'version': '17.0'},
     'filename': 'thunderbird-17.0-build3.de.win32.exe',
     'url': 'thunderbird/candidates/17.0-candidates/build3/win32/de/Thunderbird Setup 17.0.exe'},
]

tests = firefox_tests + thunderbird_tests


class ReleaseCandidateScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for ReleaseCandidateScraper"""

        for entry in tests:
            scraper = ReleaseCandidateScraper(destination=self.temp_dir,
                                              base_url=self.wdir,
                                              logger=self.logger,
                                              **entry['args'])
            expected_filename = os.path.join(self.temp_dir, entry['filename'])
            self.assertEqual(scraper.filename, expected_filename)
            self.assertEqual(urllib.unquote(scraper.url),
                             urljoin(self.wdir, entry['url']))


if __name__ == '__main__':
    unittest.main()
