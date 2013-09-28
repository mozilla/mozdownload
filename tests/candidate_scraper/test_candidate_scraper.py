#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

from mozdownload import ReleaseCandidateScraper
import mozhttpd_base_test as mhttpd

firefox_tests = [
    # -p win32 -v 21.0
    {'args': {'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.win32.exe'},
    # -a firefox -p linux -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.linux.tar.bz2'},
    # -a firefox -p linux64 -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.linux64.tar.bz2'},
    # -a firefox -p mac -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.mac.dmg'},
    # -a firefox -p win32 -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.win32.exe'},
    # -a firefox -p win32 -v 21.0 -l cs
    {'args': {'application': 'firefox',
              'locale': 'cs',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.cs.win32.exe'},
    # -a firefox -p win32 -v 21.0 -l en-GB
    {'args': {'application': 'firefox',
              'locale': 'en-GB',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-GB.win32.exe'},
    # -a firefox -p win32 -v 21.0 --build-number=1
    {'args': {'application': 'firefox',
              'build_number': '1',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build1.en-US.win32.exe'},
    # -a firefox -p win32 -v 21.0 --stub
    {'args': {'application': 'firefox',
              'is_stub_installer': True,
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.win32.exe'},
]

thunderbird_tests = [
    # -a thunderbird -p linux -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.linux.tar.bz2'},
    # -a thunderbird -p linux64 -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.linux64.tar.bz2'},
    # -a thunderbird -p mac -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.mac.dmg'},
    # -a thunderbird -p win32 -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.win32.exe'},
    # -a thunderbird -p win32 -v 10.0.5esr -l cs
    {'args': {'application': 'thunderbird',
              'locale': 'cs',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.cs.win32.exe'},
    # -a thunderbird -p win32 -v 10.0.5esr -l en-GB
    {'args': {'application': 'thunderbird',
              'locale': 'en-GB',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-GB.win32.exe'},
    # -a thunderbird -p win32 -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'build_number': '1',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build1.en-US.win32.exe'},
]

tests = firefox_tests + thunderbird_tests


class ReleaseScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for ReleaseScraper"""

        for entry in tests:
            scraper = ReleaseCandidateScraper(directory=self.temp_dir,
                                              base_url=self.wdir,
                                              **entry['args'])
            expected_target = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, expected_target)

if __name__ == '__main__':
    unittest.main()
