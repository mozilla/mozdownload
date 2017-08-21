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
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win64 --branch=mozilla-central
    {'args': {'platform': 'win64',
              'branch': 'mozilla-central'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64.installer.exe'
   },

    # -p win64 --branch=mozilla-central --date 2013-09-30 (old filename format)
    {'args': {'platform': 'win64',
              'branch': 'mozilla-central',
              'date': '2013-09-30'},
    'filename': '2013-09-30-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64-x86_64.installer.exe',
    'url': 'firefox/nightly/2013/09/2013-09-30-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64-x86_64.installer.exe'
   },

    # -p linux --branch=mozilla-central
    {'args': {'platform': 'linux',
               'branch': 'mozilla-central'},
     'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.tar.bz2',
     'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.tar.bz2'
     },

    # -p linux64 --branch=mozilla-central
    {'args': {'platform': 'linux64',
               'branch': 'mozilla-central'},
     'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-x86_64.tar.bz2',
     'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-x86_64.tar.bz2'
    },

    # -p mac --branch=mozilla-central
    {'args': {'platform': 'mac',
               'branch': 'mozilla-central'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.mac.dmg',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.mac.dmg'
    },

    # -p linux --branch=mozilla-central --extension=txt
    {'args': {'platform': 'linux',
              'branch': 'mozilla-central',
              'extension': 'txt'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.txt',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.txt'
    },

    # -p win32 --branch=mozilla-central -l it
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'locale': 'it'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.it.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.it.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central -l sv-SE
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'locale': 'sv-SE'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.sv-SE.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.sv-SE.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --build-id=20130706031213
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'build_id': '20130706031213'},
    'filename': '2013-07-06-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/07/2013-07-06-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --date=2013-07-02
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-02'},
    'filename': '2013-07-02-04-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/07/2013-07-02-04-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --date=2013-07-02 --build-number=1
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-02',
              'build_number': 1},
    'filename': '2013-07-02-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/07/2013-07-02-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=mozilla-central --stub (old format)
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-09-30',
              'is_stub_installer': True},
    'filename': '2013-09-30-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer-stub.exe',
    'url': 'firefox/nightly/2013/09/2013-09-30-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer-stub.exe'
    },

    # -p win32 --branch=mozilla-central --stub (new format)
    {'args': {'platform': 'win32',
              'branch': 'mozilla-central',
              'is_stub_installer': True},
    'filename': '2013-10-01-03-02-04-mozilla-central-Firefox Installer.en-US.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/Firefox Installer.en-US.exe'
    },

    # -p win32 --branch=mozilla-aurora
    {'args': {'platform': 'win32',
              'branch': 'mozilla-aurora'},
    'filename': '2013-10-01-03-02-04-mozilla-aurora-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-aurora/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=ux
    {'args': {'platform': 'win32',
              'branch': 'ux'},
    'filename': '2013-10-01-03-02-04-ux-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-ux/firefox-27.0a1.en-US.win32.installer.exe'
    },

    # --revision 1dbe350b57b1
    {'args': {'platform': 'win32'},
    'filename': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    'url': 'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'
    },
]

thunderbird_tests = [
    # -p linux --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'
    },

    # -p linux64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'linux64',
              'branch': 'comm-central'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2'
    },

    # -p mac --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'mac',
              'branch': 'comm-central'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.mac.dmg',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.mac.dmg'
    },

    # -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win64 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win64',
              'branch': 'comm-central'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win64-x86_64.installer.exe',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win64-x86_64.installer.exe'
    },

    # -p linux --branch=comm-central --extension=txt
    {'args': {'application': 'thunderbird',
              'platform': 'linux',
              'branch': 'comm-central',
              'extension': 'txt'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.txt',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.txt'
    },

    # -p win32 --branch=comm-central -l it
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'locale': 'it'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.it.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.it.win32.installer.exe'
    },

    # -p win32 --branch=comm-central -l sv-SE
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'locale': 'sv-SE'},
    'filename': '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.sv-SE.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.sv-SE.win32.installer.exe'
    },

    # -p win32 --branch=comm-central --build-id=20130710110153
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'build_id': '20130710110153'},
    'filename': '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=comm-central --date=2013-07-10
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'date': '2013-07-10'},
    'filename': '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=comm-central --date=2013-07-10 --build-number=1
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-central',
              'date': '2013-07-10',
              'build_number': 1},
    'filename': '2013-07-10-10-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/07/2013-07-10-10-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'
    },

    # -p win32 --branch=comm-central
    {'args': {'application': 'thunderbird',
              'platform': 'win32',
              'branch': 'comm-aurora'},
    'filename': '2013-10-01-03-02-04-comm-aurora-thunderbird-27.0a1.en-US.win32.installer.exe',
    'url': 'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-aurora/thunderbird-27.0a1.en-US.win32.installer.exe'
    },
]

b2g_tests = [
    # -p linux --branch=mozilla-central
    {'args': {'application': 'b2g',
              'platform': 'linux',
              'branch': 'mozilla-central'},
    'filename': '2014-01-12-04-02-02-mozilla-central-b2g-29.0a1.multi.linux-i686.tar.bz2',
    'url': 'b2g/nightly/2014/01/2014-01-12-04-02-02-mozilla-central/b2g-29.0a1.multi.linux-i686.tar.bz2'
     },
    # -p linux64 --branch=mozilla-central
    {'args': {'application': 'b2g',
              'platform': 'linux64',
              'branch': 'mozilla-central'},
    'filename': '2014-01-12-04-02-02-mozilla-central-b2g-29.0a1.multi.linux-x86_64.tar.bz2',
    'url': 'b2g/nightly/2014/01/2014-01-12-04-02-02-mozilla-central/b2g-29.0a1.multi.linux-x86_64.tar.bz2'
     },
    # -p mac64 --branch=mozilla-central
    {'args': {'application': 'b2g',
              'platform': 'mac64',
              'branch': 'mozilla-central'},
    'filename': '2014-01-12-04-02-02-mozilla-central-b2g-29.0a1.multi.mac64.dmg',
    'url': 'b2g/nightly/2014/01/2014-01-12-04-02-02-mozilla-central/b2g-29.0a1.multi.mac64.dmg'
     },
    # -p mac64 --branch=mozilla-central
    {'args': {'application': 'b2g',
              'platform': 'win32',
              'branch': 'mozilla-central'},
    'filename': '2014-01-12-04-02-02-mozilla-central-b2g-29.0a1.multi.win32.zip',
    'url': 'b2g/nightly/2014/01/2014-01-12-04-02-02-mozilla-central/b2g-29.0a1.multi.win32.zip'
     },
    # -p win32 --branch=mozilla-central -l en-US
    {'args': {'application': 'b2g',
              'platform': 'win32',
              'branch': 'mozilla-central',
              'locale': 'en-US'},
    'filename': '2014-01-12-04-02-02-mozilla-central-b2g-29.0a1.en-US.win32.zip',
    'url': 'b2g/nightly/2014/01/2014-01-12-04-02-02-mozilla-central/en-US/b2g-29.0a1.en-US.win32.zip'
     },
    # -p win32 --branch=mozilla-central --date=2013-07-01
    {'args': {'application': 'b2g',
              'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-01'},
    'filename': '2013-07-01-04-02-02-mozilla-central-b2g-29.0a1.multi.win32.zip',
    'url': 'b2g/nightly/2013/07/2013-07-01-04-02-02-mozilla-central/b2g-29.0a1.multi.win32.zip'
     },
    # -p win32 --branch=mozilla-central --date=2013-07-01 --build-number=1
    {'args': {'application': 'b2g',
              'platform': 'win32',
              'branch': 'mozilla-central',
              'date': '2013-07-01',
              'build_number': 1},
    'filename': '2013-07-01-04-01-01-mozilla-central-b2g-29.0a1.multi.win32.zip',
    'url': 'b2g/nightly/2013/07/2013-07-01-04-01-01-mozilla-central/b2g-29.0a1.multi.win32.zip'
     },
    # -p linux --branch=mozilla-central --build-id=20130702031336
    {'args': {'application': 'b2g',
              'platform': 'linux',
              'branch': 'mozilla-central',
              'build_id': '20130702031336'},
    'filename': '2013-07-02-03-13-36-mozilla-central-b2g-29.0a1.multi.linux-i686.tar.bz2',
    'url': 'b2g/nightly/2013/07/2013-07-02-03-13-36-mozilla-central/b2g-29.0a1.multi.linux-i686.tar.bz2'
     }
]

fennec_tests = [
    # -p android-api-9 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-api-9',
              'branch': 'mozilla-central'},
    'filename': '2016-02-01-03-02-41-mozilla-central-fennec-47.0a1.multi.android-arm.apk',
    'url': 'mobile/nightly/2016/02/2016-02-01-03-02-41-mozilla-central-android-api-9/fennec-47.0a1.multi.android-arm.apk'
    },
    # -p android-api-11 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-api-11',
              'branch': 'mozilla-central'},
    'filename': '2015-06-11-03-02-08-mozilla-central-fennec-41.0a1.multi.android-arm.apk',
    'url': 'mobile/nightly/2015/06/2015-06-11-03-02-08-mozilla-central-android-api-11/fennec-41.0a1.multi.android-arm.apk'
    },
    # -p android-api-15 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-central'},
    'filename': '2016-02-01-03-02-41-mozilla-central-fennec-47.0a1.multi.android-arm.apk',
    'url': 'mobile/nightly/2016/02/2016-02-01-03-02-41-mozilla-central-android-api-15/fennec-47.0a1.multi.android-arm.apk'
    },
    # -p android-x86 --branch=mozilla-central
    {'args': {'application': 'fennec',
              'platform': 'android-x86',
              'branch': 'mozilla-central'},
    'filename': '2016-02-01-03-02-41-mozilla-central-fennec-47.0a1.multi.android-i386.apk',
    'url': 'mobile/nightly/2016/02/2016-02-01-03-02-41-mozilla-central-android-x86/fennec-47.0a1.multi.android-i386.apk'
     },
    # -p android-api-15 --branch=mozilla-aurora
    {'args': {'application': 'fennec',
              'platform': 'android-api-15',
              'branch': 'mozilla-aurora'},
    'filename': '2016-02-02-00-40-08-mozilla-aurora-fennec-46.0a2.multi.android-arm.apk',
    'url': 'mobile/nightly/2016/02/2016-02-02-00-40-08-mozilla-aurora-android-api-15/fennec-46.0a2.multi.android-arm.apk'
    },
]

tests = firefox_tests + thunderbird_tests + b2g_tests + fennec_tests


class TestDailyScraper(mhttpd.MozHttpdBaseTest):
    """Test mozdownload daily scraper class"""

    def test_scraper(self):
        """Testing various download scenarios for DailyScraper"""

        for entry in tests:
            scraper = DailyScraper(destination=self.temp_dir,
                                   base_url=self.wdir,
                                   logger=self.logger,
                                   **entry['args'])

            expected_target = os.path.join(self.temp_dir, entry['filename'])
            self.assertEqual(scraper.filename, expected_target)
            self.assertEqual(urllib.unquote(scraper.url),
                             urljoin(self.wdir, entry['url']))


if __name__ == '__main__':
    unittest.main()
