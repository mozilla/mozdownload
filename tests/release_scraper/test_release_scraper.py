#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import ReleaseScraper
from mozdownload.utils import urljoin
import mozhttpd_base_test as mhttpd

firefox_tests = [
    # -p win32 -v latest
    {'args': {'platform': 'win32',
              'version': 'latest'},
     'target': 'firefox-latest.en-US.win32.exe',
     'target_url': 'firefox/releases/latest/win32/en-US/Firefox Setup 23.0.1.exe'},
    # -a firefox -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'firefox-latest.en-US.win32.exe',
     'target_url': 'firefox/releases/latest/win32/en-US/Firefox Setup 23.0.1.exe'},
    # -a firefox -p linux -v latest
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': 'latest'},
     'target': 'firefox-latest.en-US.linux.tar.bz2',
     'target_url': 'firefox/releases/latest/linux-i686/en-US/firefox-23.0.1.en-US.linux.tar.bz2'},
    # -a firefox -p linux64 -v latest
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': 'latest'},
     'target': 'firefox-latest.en-US.linux64.tar.bz2',
     'target_url': 'firefox/releases/latest/linux-x86_64/en-US/firefox-23.0.1.en-US.linux.tar.bz2'},
    # -a firefox -p mac -v latest
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': 'latest'},
     'target': 'firefox-latest.en-US.mac.dmg',
     'target_url': 'firefox/releases/latest/mac/en-US/firefox-23.0.1.dmg'},
    # -a firefox -p win32 -v latest -l de
    {'args': {'application': 'firefox',
              'locale': 'de',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'firefox-latest.de.win32.exe',
     'target_url': 'firefox/releases/latest/win32/de/Firefox Setup 23.0.1.exe'},
    # -a firefox -p win32 -v latest --stub
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True,
              'version': 'latest'},
     'target': 'firefox-latest.en-US.win32.exe',
     'target_url': 'firefox/releases/latest/win32/en-US/Firefox Setup Stub 23.0.1.exe'},
    # -a firefox -p win32 -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0.en-US.win32.exe',
     'target_url': 'firefox/releases/21.0/win32/en-US/Firefox Setup 21.0.exe'},
    # -a firefox -p win32 -v 21.0 -l es-ES
    {'args': {'application': 'firefox',
              'locale': 'es-ES',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0.es-ES.win32.exe',
     'target_url': 'firefox/releases/21.0/win32/es-ES/Firefox Setup 21.0.exe'}
]

thunderbird_tests = [
    # -a thunderbird -p win32 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.win32.exe',
     'target_url': 'thunderbird/releases/latest/win32/en-US/Thunderbird Setup 17.0.1.exe'},
    # -a thunderbird -p linux -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.linux.tar.bz2',
     'target_url': 'thunderbird/releases/latest/linux-i686/en-US/thunderbird-17.0.en-US.linux.tar.bz2'},
    # -a thunderbird -p linux64 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.linux64.tar.bz2',
     'target_url': 'thunderbird/releases/latest/linux-x86_64/en-US/thunderbird-17.0.en-US.linux.tar.bz2'},
    # -a thunderbird -p mac -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': 'latest'},
     'target': 'thunderbird-latest.en-US.mac.dmg',
     'target_url': 'thunderbird/releases/latest/mac/en-US/thunderbird-17.0.dmg'},
    # -a thunderbird -p win32 -v latest -l de
    {'args': {'application': 'thunderbird',
              'locale': 'de',
              'platform': 'win32',
              'version': 'latest'},
     'target': 'thunderbird-latest.de.win32.exe',
     'target_url': 'thunderbird/releases/latest/win32/de/Thunderbird Setup 17.0.1.exe'},
    # -a thunderbird -p win32 -v 16.0
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '16.0'},
     'target': 'thunderbird-16.0.en-US.win32.exe',
     'target_url': 'thunderbird/releases/16.0/win32/en-US/Thunderbird Setup 16.0.exe'},
    # -a thunderbird -p win32 -v 16.0 -l es-ES
    {'args': {'application': 'thunderbird',
              'locale': 'es-ES',
              'platform': 'win32',
              'version': '16.0'},
     'target': 'thunderbird-16.0.es-ES.win32.exe',
     'target_url': 'thunderbird/releases/16.0/win32/es-ES/Thunderbird Setup 16.0.exe'}
]

tests = firefox_tests + thunderbird_tests

DEFAULT_FILE_EXTENSIONS = {'linux': 'tar.bz2',
                           'linux64': 'tar.bz2',
                           'mac': 'dmg',
                           'mac64': 'dmg',
                           'win32': 'exe',
                           'win64': 'exe'}

class ReleaseScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for ReleaseScraper"""

        for entry in tests:
            scraper = ReleaseScraper(destination=self.temp_dir, base_url=self.wdir,
                                     log_level='ERROR', **entry['args'])
            expected_target = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, expected_target)
            self.assertEqual(urllib.unquote(scraper.final_url),
                             urljoin(self.wdir, entry['target_url']))


if __name__ == '__main__':
    unittest.main()
