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
    # -a firefox -p linux -v latest
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': 'latest'},
     'filename': 'firefox-23.0.1.en-US.linux.tar.bz2',
     'url': 'firefox/releases/23.0.1/linux-i686/en-US/firefox-23.0.1.tar.bz2'},
    # -a firefox -p linux64 -v latest
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': 'latest'},
     'filename': 'firefox-23.0.1.en-US.linux64.tar.bz2',
     'url': 'firefox/releases/23.0.1/linux-x86_64/en-US/firefox-23.0.1.tar.bz2'},
    # -a firefox -p mac -v latest
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': 'latest'},
     'filename': 'firefox-23.0.1.en-US.mac.dmg',
     'url': 'firefox/releases/23.0.1/mac/en-US/Firefox 23.0.1.dmg'},
    # -a firefox -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest'},
     'filename': 'firefox-23.0.1.en-US.win32.exe',
     'url': 'firefox/releases/23.0.1/win32/en-US/Firefox Setup 23.0.1.exe'},
    # -a firefox -p win64 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win64',
              'version': 'latest'},
     'filename': 'firefox-23.0.1.en-US.win64.exe',
     'url': 'firefox/releases/23.0.1/win64/en-US/Firefox Setup 23.0.1.exe'},

    # -a firefox -p linux -v latest-beta
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': 'latest-beta'},
     'filename': 'firefox-24.0b1.en-US.linux.tar.bz2',
     'url': 'firefox/releases/24.0b1/linux-i686/en-US/firefox-24.0b1.tar.bz2'},
    # -a firefox -p linux64 -v latest-beta
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': 'latest-beta'},
     'filename': 'firefox-24.0b1.en-US.linux64.tar.bz2',
     'url': 'firefox/releases/24.0b1/linux-x86_64/en-US/firefox-24.0b1.tar.bz2'},
    # -a firefox -p mac -v latest-beta
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': 'latest-beta'},
     'filename': 'firefox-24.0b1.en-US.mac.dmg',
     'url': 'firefox/releases/24.0b1/mac/en-US/Firefox 24.0b1.dmg'},
    # -a firefox -p win32 -v latest-beta
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest-beta'},
     'filename': 'firefox-24.0b1.en-US.win32.exe',
     'url': 'firefox/releases/24.0b1/win32/en-US/Firefox Setup 24.0b1.exe'},
    # -a firefox -p win64 -v latest-beta
    {'args': {'application': 'firefox',
              'platform': 'win64',
              'version': 'latest-beta'},
     'filename': 'firefox-24.0b1.en-US.win64.exe',
     'url': 'firefox/releases/24.0b1/win64/en-US/Firefox Setup 24.0b1.exe'},

    # -a firefox -p linux -v latest-esr
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': 'latest-esr'},
     'filename': 'firefox-24.0esr.en-US.linux.tar.bz2',
     'url': 'firefox/releases/24.0esr/linux-i686/en-US/firefox-24.0esr.tar.bz2'},
    # -a firefox -p linux64 -v latest-esr
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': 'latest-esr'},
     'filename': 'firefox-24.0esr.en-US.linux64.tar.bz2',
     'url': 'firefox/releases/24.0esr/linux-x86_64/en-US/firefox-24.0esr.tar.bz2'},
    # -a firefox -p mac -v latest-esr
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': 'latest-esr'},
     'filename': 'firefox-24.0esr.en-US.mac.dmg',
     'url': 'firefox/releases/24.0esr/mac/en-US/Firefox 24.0esr.dmg'},
    # -a firefox -p win32 -v latest-esr
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest-esr'},
     'filename': 'firefox-24.0esr.en-US.win32.exe',
     'url': 'firefox/releases/24.0esr/win32/en-US/Firefox Setup 24.0esr.exe'},
    # -a firefox -p win64 -v latest-esr
    {'args': {'application': 'firefox',
              'platform': 'win64',
              'version': 'latest-esr'},
     'filename': 'firefox-24.0esr.en-US.win64.exe',
     'url': 'firefox/releases/24.0esr/win64/en-US/Firefox Setup 24.0esr.exe'},
]

thunderbird_tests = [
    # -a thunderbird -p linux -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': 'latest'},
     'filename': 'thunderbird-17.0.en-US.linux.tar.bz2',
     'url': 'thunderbird/releases/17.0/linux-i686/en-US/thunderbird-17.0.tar.bz2'},
    # -a thunderbird -p linux64 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': 'latest'},
     'filename': 'thunderbird-17.0.en-US.linux64.tar.bz2',
     'url': 'thunderbird/releases/17.0/linux-x86_64/en-US/thunderbird-17.0.tar.bz2'},
    # -a thunderbird -p mac -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': 'latest'},
     'filename': 'thunderbird-17.0.en-US.mac.dmg',
     'url': 'thunderbird/releases/17.0/mac/en-US/Thunderbird 17.0.dmg'},
    # -a thunderbird -p win32 -v latest
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest'},
     'filename': 'thunderbird-17.0.en-US.win32.exe',
     'url': 'thunderbird/releases/17.0/win32/en-US/Thunderbird Setup 17.0.exe'},

    # -a thunderbird -p linux -v latest-beta
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': 'latest-beta'},
     'filename': 'thunderbird-20.0b1.en-US.linux.tar.bz2',
     'url': 'thunderbird/releases/20.0b1/linux-i686/en-US/thunderbird-20.0b1.tar.bz2'},
    # -a thunderbird -p linux64 -v latest-beta
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': 'latest-beta'},
     'filename': 'thunderbird-20.0b1.en-US.linux64.tar.bz2',
     'url': 'thunderbird/releases/20.0b1/linux-x86_64/en-US/thunderbird-20.0b1.tar.bz2'},
    # -a thunderbird -p mac -v latest-beta
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': 'latest-beta'},
     'filename': 'thunderbird-20.0b1.en-US.mac.dmg',
     'url': 'thunderbird/releases/20.0b1/mac/en-US/Thunderbird 20.0b1.dmg'},
    # -a thunderbird -p win32 -v latest-beta
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest-beta'},
     'filename': 'thunderbird-20.0b1.en-US.win32.exe',
     'url': 'thunderbird/releases/20.0b1/win32/en-US/Thunderbird Setup 20.0b1.exe'},

    # -a thunderbird -p linux -v latest-esr
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': 'latest-esr'},
     'filename': 'thunderbird-17.0.1esr.en-US.linux.tar.bz2',
     'url': 'thunderbird/releases/17.0.1esr/linux-i686/en-US/thunderbird-17.0.1esr.tar.bz2'},
    # -a thunderbird -p linux64 -v latest-esr
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': 'latest-esr'},
     'filename': 'thunderbird-17.0.1esr.en-US.linux64.tar.bz2',
     'url': 'thunderbird/releases/17.0.1esr/linux-x86_64/en-US/thunderbird-17.0.1esr.tar.bz2'},
    # -a thunderbird -p mac -v latest-esr
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': 'latest-esr'},
     'filename': 'thunderbird-17.0.1esr.en-US.mac.dmg',
     'url': 'thunderbird/releases/17.0.1esr/mac/en-US/Thunderbird 17.0.1esr.dmg'},
    # -a thunderbird -p win32 -v latest-esr
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': 'latest-esr'},
     'filename': 'thunderbird-17.0.1esr.en-US.win32.exe',
     'url': 'thunderbird/releases/17.0.1esr/win32/en-US/Thunderbird Setup 17.0.1esr.exe'},
]

tests = firefox_tests + thunderbird_tests


class ReleaseScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_latest_build(self):
        """Testing various download scenarios for latest release builds"""

        for entry in tests:
            scraper = ReleaseScraper(destination=self.temp_dir,
                                     base_url=self.wdir,
                                     logger=self.logger,
                                     **entry['args'])
            expected_filename = os.path.join(self.temp_dir, entry['filename'])
            self.assertEqual(scraper.filename, expected_filename)
            self.assertEqual(urllib.unquote(scraper.url),
                             urljoin(self.wdir, entry['url']))


if __name__ == '__main__':
    unittest.main()
