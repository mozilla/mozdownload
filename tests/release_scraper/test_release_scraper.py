#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

from mozdownload import ReleaseScraper
import mozhttpd_base_test as mhttpd

BUILD_TYPES = {'release': ReleaseScraper}

firefox_tests = [
    # -p win32 -v latest
    {'args': {'platform': 'win32',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.win32.exe'},
    # -t release -p win32 -v latest
    {'args': {'platform': 'win32',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.win32.exe',
    'type': 'release'},
    # -a firefox -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.win32.exe',
    'type': 'release'},
    # -a firefox -t release -p linux -v latest
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.linux.tar.bz2',
    'type': 'release'},
    # -a firefox -t release -p linux64 -v latest
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.linux64.tar.bz2',
    'type': 'release'},
    # -a firefox -t release -p mac -v latest
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.mac.dmg',
    'type': 'release'},
    # -a firefox -t release -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest'},
    'target': 'firefox-latest.en-US.win32.exe',
    'type': 'release'},
    # -a firefox -t release -p win32 -v latest -l de
    {'args': {'application': 'firefox',
              'locale': 'de',
              'platform': 'win32',
              'version': 'latest'},
    'target': 'firefox-latest.de.win32.exe',
    'type': 'release'},
    # -a firefox -t release -p win32 -v latest --stub
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True,
              'version': 'latest'},
     'target': 'firefox-latest.en-US.win32.exe',
     'type': 'release'},
    # -a firefox -t release -p win32 -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0.en-US.win32.exe',
     'type': 'release'},
    # -a firefox -t release -p win32 -v 21.0 -l es-ES
    {'args': {'application': 'firefox',
              'locale': 'es-ES',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0.es-ES.win32.exe',
     'type': 'release'}
]

thunderbird_tests = [
    # -a thunderbird -p win32 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.win32.exe'},
    # -a thunderbird -t release -p linux -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.linux.tar.bz2',
     'type': 'release'},
    # -a thunderbird -t release -p linux64 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.linux64.tar.bz2',
     'type': 'release'},
    # -a thunderbird -t release -p mac -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.mac.dmg',
     'type': 'release'},
    # -a thunderbird -t release -p win32 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.win32.exe',
     'type': 'release'},
    # -a thunderbird -t release -p win32 -v latest -l de
    {'args': {'application': 'thunderbird',
              'locale': 'de',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'thunderbird-latest.de.win32.exe',
     'type': 'release'},
    # -a thunderbird -t release -p win32 -v 16.0
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '16.0'},
     'target': 'thunderbird-16.0.en-US.win32.exe',
     'type': 'release'},
    # -a thunderbird -t release -p win32 -v 16.0 -l es-ES
    {'args': {'application': 'thunderbird',
              'locale': 'es-ES',
              'platform': 'win32',
              'version': '16.0'},
     'target': 'thunderbird-16.0.es-ES.win32.exe',
     'type': 'release'}
]

tests = firefox_tests + thunderbird_tests


class ReleaseScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for ReleaseScraper"""

        for entry in tests:
            # Mimick real case scenario
            if entry.get('type'):
                scraper = BUILD_TYPES[entry['type']](directory=self.temp_dir,
                                                     base_url=self.wdir,
                                                     **entry['args'])
            else:
                scraper = ReleaseScraper(directory=self.temp_dir,
                                         base_url=self.wdir, **entry['args'])

            target_cmp = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, target_cmp)

if __name__ == '__main__':
    unittest.main()
