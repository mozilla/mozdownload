#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest
import urllib

from mozdownload import DailyScraper
from mozdownload.utils import urljoin
import mozhttpd_base_test as mhttpd

firefox_tests = [
    # -p win32
    {'args': {'platform': 'win32'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win64 --branch=mozilla-central
    {'args': {'platform': 'win64',
              'branch': 'mozilla-central'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64-x86_64.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64-x86_64.installer.exe'
   },

    # -p linux --branch=mozilla-central
    {'args': {'platform': 'linux',
               'branch': 'mozilla-central'},
     'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.tar.bz2',
     'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.tar.bz2'
     },

    # -p linux64 --branch=mozilla-central
    {'args': {'platform': 'linux64',
               'branch': 'mozilla-central'},
     'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-x86_64.tar.bz2',
     'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-x86_64.tar.bz2'
    },

    # -p mac --branch=mozilla-central
    {'args': {'platform': 'mac',
               'branch': 'mozilla-central'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.mac.dmg',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.mac.dmg'
    },

    # -p linux --branch=mozilla-central --extension=txt
    {'args': {'platform': 'linux',
              'branch': 'mozilla-central',
              'extension': 'txt'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.txt',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.txt'
    },

    # -p win32 --branch=mozilla-central -l it
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'locale': 'it'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.it.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.it.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central -l sv-SE
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'locale': 'sv-SE'},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.sv-SE.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.sv-SE.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --build-id=20130706031213
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20130706031213'},
    'target': '2013-07-06-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/07/2013-07-06-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --date=2013-07-02
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-02'},
    'target': '2013-07-02-04-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/07/2013-07-02-04-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --date=2013-07-02 --build-number=1
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-02',
              'build_number': 1},
    'target': '2013-07-02-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/07/2013-07-02-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --stub
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'is_stub_installer': True},
    'target': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer-stub.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer-stub.exe'
    },

    # -p win32 --branch=mozilla-aurora
    {'args': {'platform': 'win32',
              'branch': 'mozilla-aurora'},
    'target': '2013-10-01-03-02-04-mozilla-aurora-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-aurora/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=ux
    {'args': {'platform': 'win32',
              'branch': 'ux'},
    'target': '2013-10-01-03-02-04-ux-firefox-27.0a1.en-US.win32.installer.exe',
    'target_url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-ux/firefox-27.0a1.en-US.win32.installer.exe'
    },
]

thunderbird_tests = [
    # -p linux --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'
    },

    # -p linux64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'branch': 'comm-central'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2'
    },

    # -p mac --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'branch': 'comm-central'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.mac.dmg',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.mac.dmg'
    },

    # -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win64',
              'branch': 'comm-central'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win64-x86_64.installer.exe',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win64-x86_64.installer.exe'
    },

    # -p linux --branch=comm-central --extension=txt
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central',
              'extension': 'txt'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.txt',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.txt'
    },

    # -p win32 --branch=comm-central -l it
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'locale': 'it'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.it.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.it.win32.installer.exe'
    },

    # -p win32 --branch=comm-central -l sv-SE
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'locale': 'sv-SE'},
    'target': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.sv-SE.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.sv-SE.win32.installer.exe'
    },

    # -p win32 --branch=comm-central --build-id=20130710110153
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'build_id': '20130710110153'},
    'target': '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=comm-central --date=2013-07-10
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'date': '2013-07-10'},
    'target': '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=comm-central --date=2013-07-10 --build-number=1
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'date': '2013-07-10',
              'build_number': 1},
    'target': '2013-07-10-10-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/07/2013-07-10-10-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-aurora'},
    'target': '2013-10-01-03-02-04-comm-aurora-thunderbird-27.0a1.en-US.win32.installer.exe',
    'target_url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-aurora/thunderbird-27.0a1.en-US.win32.installer.exe'
    },
]

tests = firefox_tests + thunderbird_tests


class DailyScraperTest(mhttpd.MozHttpdBaseTest):
    """Test mozdownload daily scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for DailyScraper"""

        for entry in tests:
            scraper = DailyScraper(directory=self.temp_dir, base_url=self.wdir,
                                   version=None, log_level='ERROR',
                                   **entry['args'])
            expected_target = os.path.join(self.temp_dir, entry['target'])
            self.assertEqual(scraper.target, expected_target)
            self.assertEqual(urllib.unquote(scraper.final_url),
                urljoin(self.wdir, entry['target_url']))


if __name__ == '__main__':
    unittest.main()
