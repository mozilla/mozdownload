#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import tempfile
import unittest
import urllib

import mozfile

import mozdownload
from mozdownload.scraper import BASE_URL
from mozdownload.utils import urljoin


tests_release_scraper = [
    # -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest'}},

    # -p win32 -v 42.0b2
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/win32/en-US/Firefox Setup 42.0b2.exe'},

    # -p win64 -v 42.0b2
    {'args': {'application': 'firefox',
              'platform': 'win64',
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/win64/en-US/Firefox Setup 42.0b2.exe'},

    # -p linux -v 42.0b2
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/linux-i686/en-US/firefox-42.0b2.tar.bz2'},

    # -a firefox -p linux64 -v 42.0b2
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/linux-x86_64/en-US/firefox-42.0b2.tar.bz2'},

    # -a firefox -p mac -v 42.0b2
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/mac/en-US/Firefox 42.0b2.dmg'},

    # -a firefox -p win32 -v 42.0b2 -l de
    {'args': {'application': 'firefox',
              'locale': 'de',
              'platform': 'win32',
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/win32/de/Firefox Setup 42.0b2.exe'},

    # -a firefox -p win32 -v 42.0b2 --stub (old format)
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True,
              'version': '42.0b2'},
     'url': 'firefox/releases/42.0b2/win32/en-US/Firefox Setup Stub 42.0b2.exe'},

    # -a firefox -p win32 -v 55.0 --stub (new format)
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True,
              'version': '55.0'},
     'url': 'firefox/releases/55.0/win32/en-US/Firefox Installer.exe'},
]

tests_candidate_scraper = [
    # -p win32 -v 45.4.0esr --build-number=1
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/win32/en-US/Firefox Setup 45.4.0esr.exe'},

    # -a firefox -p win32 -v 45.4.0esr --build-number=1 --extension json
    {'args': {'application': 'firefox',
              'extension': 'json',
              'platform': 'win32',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/win32/en-US/firefox-45.4.0esr.json'},

    # -a firefox -p linux -v 45.4.0esr --build-number=1
    {'args': {'application': 'firefox',
              'platform': 'linux',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/linux-i686/en-US/firefox-45.4.0esr.tar.bz2'},

    # -a firefox -p linux -v 45.4.0esr --build-number=1 --extension json
    {'args': {'application': 'firefox',
              'extension': 'json',
              'platform': 'linux',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/linux-i686/en-US/firefox-45.4.0esr.json'},

    # -a firefox -p linux64 -v 45.4.0esr --build-number=1
    {'args': {'application': 'firefox',
              'platform': 'linux64',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/linux-x86_64/en-US/firefox-45.4.0esr.tar.bz2'},

    # -a firefox -p linux64 -v 45.4.0esr --build-number=1 --extension json
    {'args': {'application': 'firefox',
              'extension': 'json',
              'platform': 'linux64',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/linux-x86_64/en-US/firefox-45.4.0esr.json'},

    # -a firefox -p mac -v 45.4.0esr --build-number=1
    {'args': {'application': 'firefox',
              'platform': 'mac',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/mac/en-US/Firefox 45.4.0esr.dmg'},

    # -a firefox -p mac -v 45.4.0esr --build-number=1 --extension json
    {'args': {'application': 'firefox',
              'extension': 'json',
              'platform': 'mac',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/mac/en-US/firefox-45.4.0esr.json'},

    # -a firefox -p win32 -v 45.4.0esr -l de --build-number=1
    {'args': {'application': 'firefox',
              'locale': 'de',
              'platform': 'win32',
              'version': '45.4.0esr',
              'build_number': 1},
     'url': 'firefox/candidates/45.4.0esr-candidates/build1/win32/de/Firefox Setup 45.4.0esr.exe'},

    # -a firefox -p win32 -v 52.0 --build-number=1 --stub (old format)
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True,
              'version': '52.0',
              'build_number': 1},
     'url': 'firefox/candidates/52.0-candidates/build1/win32/en-US/Firefox Setup Stub 52.0.exe'},

    # -a firefox -p win32 -v 55.0 --build-number=1 --stub (new format)
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'is_stub_installer': True,
              'version': '55.0',
              'build_number': 1},
     'url': 'firefox/candidates/55.0-candidates/build1/win32/en-US/Firefox Installer.exe'},
]

tests_daily_scraper = [
    # -p win32 --branch=mozilla-central
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central'}},

    # -p win64 --branch=mozilla-central
    {'args': {'platform': 'win64',
              'branch': 'mozilla-central'}},

    # -p linux --branch=mozilla-central
    {'args': {'platform': 'linux',
              'branch': 'mozilla-central'}},

    # -p linux64 --branch=mozilla-central
    {'args': {'platform': 'linux64',
              'branch': 'mozilla-central'}},

    # -p mac --branch=mozilla-central
    {'args': {'platform': 'mac',
              'branch': 'mozilla-central'}},

    # -p win32 --branch=mozilla-central --date 2015-10-21
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2015-10-21'}},

    # -p win32 --branch=mozilla-central --date=2015-10-21 --build-number=2
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2015-10-21',
              'build_number': 2}},

    # -p win32 --branch=mozilla-central --build-id=20151021030212
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20151021065025'}},

    # -p win32 --branch=mozilla-central --build-id=20151021030212 --locale=de
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20151021030212',
              'locale': 'de'}},

    # -p linux --branch=mozilla-central --build-id=20151021030212 --extension=txt
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20151021030212',
              'extension': 'txt'}},

    # -p win32 --branch=mozilla-central --build-id=20151021030212 --stub (old format)
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20151021030212',
              'is_stub_installer': True}},

    # -p win32 --branch=mozilla-central --build-id=20170821100350 --stub (new format)
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20170821100350',
              'is_stub_installer': True}},

    # -p win64 --branch=mozilla-central --build-id=20170821100350 --stub (new format)
    {'args': {'platform': 'win64',
              'branch': 'mozilla-central',
              'build_id': '20170821100350',
              'is_stub_installer': True}},
]

tests_tinderbox_scraper = [
    # -p win32 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'win32'}},

    # -p win64 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'win64'}},

    # -p linux --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux'}},

    # -p linux64 --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux64'}},

    # -p mac --branch=mozilla-central
    {'args': {'branch': 'mozilla-central',
              'platform': 'mac'}},

    # -p win32 --branch=mozilla-central --debug-build
    {'args': {'branch': 'mozilla-central',
              'platform': 'win32',
              'debug_build': True}},

    # -p win32 --branch=mozilla-central --locale=de
    {'args': {'branch': 'mozilla-central',
              'platform': 'win32',
              'locale': 'de'}},

    # -p linux --branch=mozilla-central --extension=txt
    {'args': {'branch': 'mozilla-central',
              'platform': 'linux',
              'extension': 'txt'}},

    # -p win32 --branch=mozilla-beta
    {'args': {'branch': 'mozilla-beta',
              'platform': 'win32'}},
]


class FirefoxRemoteTests(unittest.TestCase):
    """Test all scraper classes for Firefox against the remote server"""

    def setUp(self):
        logging.basicConfig(format=' %(levelname)s | %(message)s', level=logging.ERROR)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create a temporary directory for potential downloads
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        mozfile.rmtree(self.temp_dir)

    def test_release_scraper(self):
        for test in tests_release_scraper:
            scraper = mozdownload.ReleaseScraper(destination=self.temp_dir,
                                                 logger=self.logger,
                                                 **test['args'])
            if test.get('url'):
                self.assertEqual(urllib.unquote(scraper.url),
                                 urljoin(BASE_URL, test['url']))

    def test_candidate_scraper(self):
        for test in tests_candidate_scraper:
            scraper = mozdownload.ReleaseCandidateScraper(destination=self.temp_dir,
                                                          logger=self.logger,
                                                          **test['args'])
            if test.get('url'):
                self.assertEqual(urllib.unquote(scraper.url),
                                 urljoin(BASE_URL, test['url']))

    def test_daily_scraper(self):
        for test in tests_daily_scraper:
            mozdownload.DailyScraper(destination=self.temp_dir,
                                     logger=self.logger,
                                     **test['args'])

    def test_tinderbox_scraper(self):
        for test in tests_tinderbox_scraper:
            mozdownload.TinderboxScraper(destination=self.temp_dir,
                                         logger=self.logger,
                                         **test['args'])

    @unittest.skip('Not testable as long as we cannot grab a latest build')
    def test_try_scraper(self):
        pass

if __name__ == '__main__':
    unittest.main()
