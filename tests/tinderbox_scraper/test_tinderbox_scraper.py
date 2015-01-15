#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import TinderboxScraper
from mozdownload.utils import urljoin
import mozhttpd_base_test as mhttpd

firefox_tests = [
    # -p win32
    {'args': {'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -p win32 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32
    {'args': {'application': 'firefox',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --stub
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer-stub.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer-stub.exe'},
    # -a firefox -p linux --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.linux-i686.tar.bz2',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-linux/'
                   '1374583608/firefox-25.0a1.en-US.linux-i686.tar.bz2'},
    # -a firefox -p linux64 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux64'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.linux-x86_64.tar.bz2',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-linux64/'
                   '1374583608/firefox-25.0a1.en-US.linux-x86_64.tar.bz2'},
    # -a firefox -p win32 --branch=mozilla-central
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win64 --branch=mozilla-central
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'platform': 'win64'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win64-x86_64.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win64/'
                   '1374583608/firefox-25.0a1.en-US.win64-x86_64.installer.exe'},
    # -a firefox -p mac64 --branch=mozilla-central
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'platform': 'mac64'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.mac.dmg',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-macosx64/'
                   '1374583608/firefox-25.0a1.en-US.mac.dmg'},
    # -a firefox -p win32 --branch=mozilla-central --debug-build
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'debug_build': True,
              'platform': 'win32'},
     'target': 'mozilla-central-debug-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32-debug/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central -l de
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'locale': 'de',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.de.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-l10n/'
                   'firefox-25.0a1.de.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central -l pt-PT
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'locale': 'pt-PT',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.pt-PT.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-l10n/'
                   'firefox-25.0a1.pt-PT.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central --date=2013-07-23
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'date': '2013-07-23',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central --date=2013-07-23 --build-number=1
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'build_number': '1',
              'date': '2013-07-23',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374568307/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central --date=1374573725
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'date': '1374573725',
              'platform': 'win32'},
     'target': '1374573725-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-win32/'
                   '1374573725/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-inbound
    {'args': {'application': 'firefox',
              'branch': 'mozilla-inbound',
              'platform': 'win32'},
     'target': 'mozilla-inbound-firefox-25.0a1.en-US.win32.installer.exe',
     'target_url': 'firefox/tinderbox-builds/mozilla-inbound-win32/'
                   '1374583608/firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -t tinderbox -p linux --branch=mozilla-central --extension=txt
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'extension': 'txt',
              'platform': 'linux'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.linux-i686.txt',
     'target_url': 'firefox/tinderbox-builds/mozilla-central-linux/'
                   '1374583608/firefox-25.0a1.en-US.linux-i686.txt'},
]

thunderbird_tests = [
    # -a thunderbird -p linux --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'linux'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-linux/'
                   '1380362686/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'},
    # -a thunderbird -p linux64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'linux64'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-linux64/'
                   '1380362686/thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2'},
    # -a thunderbird -p mac64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'mac64'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.mac.dmg',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-macosx64/'
                   '1380362686/thunderbird-27.0a1.en-US.mac.dmg'},
    # -a thunderbird -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'win32'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-win32/'
                   '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'},
    # -a thunderbird -p win64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'platform': 'win64'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.win64-x86_64.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-win64/'
                   '1380362686/thunderbird-27.0a1.en-US.win64-x86_64.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-central --debug-build
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'debug_build': True,
              'platform': 'win32'},
     'target': 'comm-central-debug-thunderbird-27.0a1.en-US.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-win32-debug/'
                   '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-central -l de
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'locale': 'de',
              'platform': 'win32'},
     'target': 'comm-central-thunderbird-27.0a1.de.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-l10n/'
                   'thunderbird-27.0a1.de.win32.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-central -l pt-PT
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'locale': 'pt-PT',
              'platform': 'win32'},
     'target': 'comm-central-thunderbird-27.0a1.pt-PT.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-l10n/'
                   'thunderbird-27.0a1.pt-PT.win32.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-central --date=2013-09-28
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'date': '2013-09-28',
              'platform': 'win32'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-win32/'
                   '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-central --date=2013-07-24 --build-number=1
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'build_number': '1',
              'date': '2013-09-28',
              'platform': 'win32'},
     'target': 'comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-win32/'
                   '1380362527/thunderbird-27.0a1.en-US.win32.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-central --date=1380362527
    {'args': {'application': 'thunderbird',
              'branch': 'comm-central',
              'date': '1380362527',
              'platform': 'win32'},
     'target': '1380362527-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-central-win32/'
                   '1380362527/thunderbird-27.0a1.en-US.win32.installer.exe'},
    # -a thunderbird -p win32 --branch=comm-aurora
    {'args': {'application': 'thunderbird',
              'branch': 'comm-aurora',
              'platform': 'win32'},
     'target': 'comm-aurora-thunderbird-27.0a1.en-US.win32.installer.exe',
     'target_url': 'thunderbird/tinderbox-builds/comm-aurora-win32/'
                   '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'}
]

tests = firefox_tests + thunderbird_tests

DEFAULT_FILE_EXTENSIONS = {'linux': 'tar.bz2',
                           'linux64': 'tar.bz2',
                           'mac': 'dmg',
                           'mac64': 'dmg',
                           'win32': 'exe',
                           'win64': 'exe'}


class TinderboxScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload TinderboxScraper class"""

    def test_scraper(self):
        """Testing various download scenarios for TinderboxScraper"""

        for entry in tests:
            scraper = TinderboxScraper(destination=self.temp_dir, version=None,
                                       base_url=self.wdir, log_level='ERROR',
                                       **entry['args'])
            expected_target = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, expected_target)
            destination_ext = DEFAULT_FILE_EXTENSIONS[entry['args']['platform']]
            if 'extension' in entry['args']:
                destination_ext = entry['args']['extension']
            destination = os.path.join(self.temp_dir, "file." + destination_ext)
            scraper2 = TinderboxScraper(destination=destination, version=None,
                                       base_url=self.wdir, log_level='ERROR',
                                       **entry['args'])
            expected_target = destination
            self.assertEqual(scraper2.target, expected_target)
            self.assertEqual(urllib.unquote(scraper.final_url),
                             urljoin(self.wdir, entry['target_url']))

if __name__ == '__main__':
    unittest.main()
