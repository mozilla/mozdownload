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
    # -p win32 -v 21.0
    {'args': {'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.win32.exe',
     'target_url': 'firefox/candidates/21.0-candidates/build3/win32/en-US/Firefox Setup 21.0.exe'},
    # -a firefox -p linux -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.linux.tar.bz2',
     'target_url': 'firefox/candidates/21.0-candidates/build3/linux-i686/en-US/firefox-21.0.tar.bz2'},
    # -a firefox -p linux64 -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.linux64.tar.bz2',
     'target_url': 'firefox/candidates/21.0-candidates/build3/linux-x86_64/en-US/firefox-21.0.tar.bz2'},
    # -a firefox -p mac -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.mac.dmg',
     'target_url': 'firefox/candidates/21.0-candidates/build3/mac/en-US/Firefox 21.0.dmg'},
    # -a firefox -p win32 -v 21.0
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.win32.exe',
     'target_url': 'firefox/candidates/21.0-candidates/build3/win32/en-US/Firefox Setup 21.0.exe'},
    # -a firefox -p win32 -v 21.0 -l cs
    {'args': {'application': 'firefox',
              'locale': 'cs',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.cs.win32.exe',
     'target_url': 'firefox/candidates/21.0-candidates/build3/win32/cs/Firefox Setup 21.0.exe'},
    # -a firefox -p win32 -v 21.0 -l en-GB
    {'args': {'application': 'firefox',
              'locale': 'en-GB',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-GB.win32.exe',
     'target_url': 'firefox/candidates/21.0-candidates/build3/win32/en-GB/Firefox Setup 21.0.exe'},
    # -a firefox -p win32 -v 21.0 --build-number=1
    {'args': {'application': 'firefox',
              'build_number': '1',
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build1.en-US.win32.exe',
     'target_url': 'firefox/candidates/21.0-candidates/build1/win32/en-US/Firefox Setup 21.0.exe'},
    # -a firefox -p win32 -v 21.0 --stub
    {'args': {'application': 'firefox',
              'is_stub_installer': True,
              'platform': 'win32',
              'version': '21.0'},
     'target': 'firefox-21.0-build3.en-US.win32.exe',
     'target_url': 'firefox/candidates/21.0-candidates/build3/win32/en-US/Firefox Setup Stub 21.0.exe'},
    # -p win64 -v 37.0b1
    {'args': {'platform': 'win64',
              'version': '37.0b1'},
     'target': 'firefox-37.0b1-build1.en-US.win64.exe',
     'target_url': 'firefox/candidates/37.0b1-candidates/build1/win64/en-US/Firefox Setup 37.0b1.exe'},
]

thunderbird_tests = [
    # -a thunderbird -p linux -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.linux.tar.bz2',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build3/linux-i686/en-US/thunderbird-10.0.5esr.tar.bz2'},
    # -a thunderbird -p linux64 -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.linux64.tar.bz2',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build3/linux-x86_64/en-US/thunderbird-10.0.5esr.tar.bz2'},
    # -a thunderbird -p mac -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.mac.dmg',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build3/mac/en-US/Thunderbird 10.0.5esr.dmg'},
    # -a thunderbird -p win32 -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-US.win32.exe',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build3/win32/en-US/Thunderbird Setup 10.0.5esr.exe'},
    # -a thunderbird -p win32 -v 10.0.5esr -l cs
    {'args': {'application': 'thunderbird',
              'locale': 'cs',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.cs.win32.exe',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build3/win32/cs/Thunderbird Setup 10.0.5esr.exe'},
    # -a thunderbird -p win32 -v 10.0.5esr -l en-GB
    {'args': {'application': 'thunderbird',
              'locale': 'en-GB',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build3.en-GB.win32.exe',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build3/win32/en-GB/Thunderbird Setup 10.0.5esr.exe'},
    # -a thunderbird -p win32 -v 10.0.5esr
    {'args': {'application': 'thunderbird',
              'build_number': '1',
              'platform': 'win32',
              'version': '10.0.5esr'},
     'target': 'thunderbird-10.0.5esr-build1.en-US.win32.exe',
     'target_url': 'thunderbird/candidates/10.0.5esr-candidates/build1/win32/en-US/Thunderbird Setup 10.0.5esr.exe'},
]

tests = firefox_tests + thunderbird_tests


class ReleaseCandidateScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for ReleaseCandidateScraper"""

        for entry in tests:
            scraper = ReleaseCandidateScraper(directory=self.temp_dir,
                                              base_url=self.wdir,
                                              log_level='ERROR',
                                              **entry['args'])
            expected_target = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, expected_target)
            self.assertEqual(urllib.unquote(scraper.final_url),
                             urljoin(self.wdir, entry['target_url']))


if __name__ == '__main__':
    unittest.main()
