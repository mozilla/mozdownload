#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# TODO:
# - Check the regex, too, so that looking for the right file

import os
import unittest

from mozdownload import ReleaseScraper
import mozhttpd_base_test as mhttpd

# Mimicking real case scenario
BUILD_TYPES = {'release': ReleaseScraper}


class ReleaseScraperTest(mhttpd.MozHttpdBaseTest):
    """test mozdownload scraper class"""

    def test_firefox_binaries(self):
        """Testing various download scenarios for the ReleaseScraper Class"""

        release_tests = [
            # -p win32 -v latest
            {'args': {'platform': 'win32',
                      'version': 'latest'},
             'target':'firefox-latest.en-US.win32.exe'},
             # -t release -p win32 -v latest
             {'args': {'platform': 'win32',
                       'version': 'latest'},
             'target':'firefox-latest.en-US.win32.exe',
             'type': 'release'},
             # -a firefox -p win32 -v latest
             {'args': {'application': 'firefox',
                       'platform': 'win32',
                       'version': 'latest'},
             'target':'firefox-latest.en-US.win32.exe',
             'type': 'release'},
             # -a firefox -t release -p linux -v latest
             {'args': {'application': 'firefox',
                       'platform': 'linux',
                       'version': 'latest'},
             'target':'firefox-latest.en-US.linux.tar.bz2',
             'type': 'release'},
             # -a firefox -t release -p linux64 -v latest
             {'args': {'application': 'firefox',
                       'platform': 'linux64',
                       'version': 'latest'},
             'target':'firefox-latest.en-US.linux64.tar.bz2',
             'type': 'release'},
             # -a firefox -t release -p mac -v latest
             {'args': {'application': 'firefox',
                       'platform': 'mac',
                       'version': 'latest'},
             'target':'firefox-latest.en-US.mac.dmg',
             'type': 'release'},
             # -a firefox -t release -p win32 -v latest
             {'args': {'application': 'firefox',
                       'platform': 'win32',
                       'version': 'latest'},
             'target':'firefox-latest.en-US.win32.exe',
             'type': 'release'},
             # -a firefox -t release -p win32 -v latest -l de
             {'args': {'application': 'firefox',
                       'locale': 'de',
                       'platform': 'win32',
                       'version': 'latest'},
             'target':'firefox-latest.de.win32.exe',
             'type': 'release'},
             # -a firefox -t release -p win32 -v latest --stub
             {'args': {'application': 'firefox',
                       'platform': 'win32',
                       'is_stub_installer': True,
                       'version': 'latest'},
              'target':'firefox-latest.en-US.win32.exe',
              'type': 'release'},
             # -a firefox -t release -p win32 -v 21.0
             {'args': {'application': 'firefox',
                       'platform': 'win32',
                       'version': '21.0'},
              'target':'firefox-21.0.en-US.win32.exe',
              'type': 'release'},
             # -a firefox -t release -p win32 -v 21.0 -l es-ES
             {'args': {'application': 'firefox',
                       'locale': 'es-ES',
                       'platform': 'win32',
                       'version': '21.0'},
              'target':'firefox-21.0.es-ES.win32.exe',
              'type': 'release'}
              ]

        for entry in release_tests:
            if entry.get('type'):
                scraper = BUILD_TYPES[entry['type']](directory=self.temp_dir,
                                                     base_url=self.wdir,
                                                     **entry['args'])
            else:
                scraper = ReleaseScraper(directory=self.temp_dir,
                                         base_url=self.wdir, **entry['args'])
    
            target_cmp = os.path.join(self.temp_dir,
                                      entry['target'])
            self.assertEqual(scraper.target, target_cmp)

if __name__ == '__main__':
    unittest.main()
