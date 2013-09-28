#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

from mozdownload import TinderboxScraper
from mozdownload.utils import create_md5
import mozhttpd_base_test as mhttpd

firefox_tests = [
    # -p win32
    {'args': {'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -p win32 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32
    {'args': {'application': 'firefox',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p linux --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.linux-i686.tar.bz2'},
    # -a firefox -p linux64 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux64'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.linux-x86_64.tar.bz2'},
    # TODO: uncomment once Issue #144 is solved
    # TODO: https://github.com/mozilla/mozdownload/issues/144
    # -a firefox -p mac64 --branch=mozilla-central
    #{'args': {'platform': 'mac64',
    #          'branch': 'mozilla-central'},
    # 'target': 'mozilla-central-firefox-25.0a1.en-US.mac.dmg'},
    # -a firefox -p win32 --branch=mozilla-central
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win64 --branch=mozilla-central
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'platform': 'win64'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win64-x86_64.installer.exe'},
    # -a firefox -p linux --branch=mozilla-central --extension=txt
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'extension': 'txt',
              'platform': 'linux'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.linux-i686.txt'},
    # -a firefox -p win32 --branch=mozilla-central --debug-build
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'debug_build': True,
              'platform': 'win32'},
     'target': 'mozilla-central-debug-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central -l de
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'locale': 'de',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.de.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central -l pt-PT
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'locale': 'pt-PT',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.pt-PT.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central --date=2013-07-23
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'date': '2013-07-23',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central --date=2013-07-23 --build-number=1
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'build_number': '1',
              'date': '2013-07-23',
              'platform': 'win32'},
     'target': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-central --date=1374141721
    {'args': {'application': 'firefox',
              'branch': 'mozilla-central',
              'date': '1374573725',
              'platform': 'win32'},
     'target': '1374573725-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},
    # -a firefox -p win32 --branch=mozilla-inbound
    {'args': {'application': 'firefox',
              'branch': 'mozilla-inbound',
              'platform': 'win32'},
     'target': 'mozilla-inbound-firefox-25.0a1.en-US.win32.installer.exe'},
]

thunderbird_tests = [
    # -a thunderbird -p linux --branch=comm-central
    # -a thunderbird -p linux64 --branch=comm-central
    # -a thunderbird -p mac64 --branch=comm-central
    # -a thunderbird -p win32 --branch=comm-central
    # -a thunderbird -p win64 --branch=comm-central
    # -a thunderbird -p linux --branch=comm-central --extension=txt
    # -a thunderbird -p win32 --branch=comm-central --debug-build
    # -a thunderbird -p win32 --branch=comm-central -d thunderbird-tinderbox-builds
    # -a thunderbird -p win32 --branch=comm-central -l el
    # -a thunderbird -p win32 --branch=comm-central -l pt-PT
    # -a thunderbird -p win32 --branch=comm-central --date=2013-07-24
    # -a thunderbird -p win32 --branch=comm-central --date=2013-07-24 --build-number=1
    # -a thunderbird -p win32 --branch=comm-central --date=1374660125
    # -a thunderbird -p win32 --branch=comm-aurora
]

tests = firefox_tests + thunderbird_tests


class TinderboxScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload TinderboxScraper class"""

    def test_scraper(self):
        """Testing various download scenarios for TinderboxScraper"""

        for entry in tests:
            scraper = TinderboxScraper(directory=self.temp_dir, version=None,
                                       base_url=self.wdir, **entry['args'])
            expected_target = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, expected_target)
            # Check if correct build was downloaded
            # Chosen build is larger than the other options
            if entry['args'].get('build_number') or \
                    entry['args'].get('date') == '1374568307':
                scraper.download()
                f_path = os.path.join(mhttpd.HERE, mhttpd.WDIR, 'firefox',
                                      'tinderbox-builds',
                                      'mozilla-central-win32', '1374568307',
                                      'firefox-25.0a1.en-US.win32.installer.exe')
                md5_original = create_md5(f_path)
                md5_downloaded = create_md5(os.path.join(self.temp_dir,
                                                         entry['target']))
                self.assertEqual(md5_original, md5_downloaded)

if __name__ == '__main__':
    unittest.main()
