#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
from six.moves.urllib.parse import unquote

from mozdownload import DailyScraper
from mozdownload.utils import urljoin

firefox_tests = [
    ({'platform': 'win32'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win32', 'branch': 'mozilla-central'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win64', 'branch': 'mozilla-central'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64.installer.exe'),
    ({'platform': 'linux', 'branch': 'mozilla-central'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.tar.bz2',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'platform': 'linux64', 'branch': 'mozilla-central'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-x86_64.tar.bz2',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'platform': 'mac', 'branch': 'mozilla-central'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.mac.dmg',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.mac.dmg'),
    ({'platform': 'linux', 'branch': 'mozilla-central', 'extension': 'txt'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.txt',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.txt'),
    ({'platform': 'win32', 'branch': 'mozilla-central', 'locale': 'it'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.it.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.it.win32.installer.exe'),
    ({'platform': 'win32', 'branch': 'mozilla-central', 'locale': 'sv-SE'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.sv-SE.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.sv-SE.win32.installer.exe'),
    ({'platform': 'win32', 'branch': 'mozilla-central', 'build_id': '20130706031213'},
     '2013-07-06-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/07/2013-07-06-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win32', 'branch': 'mozilla-central', 'date': '2013-07-02'},
     '2013-07-02-04-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/07/2013-07-02-04-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win32', 'branch': 'mozilla-central', 'date': '2013-07-02', 'build_number': 1},
     '2013-07-02-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/07/2013-07-02-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    # Old stub format
    ({'platform': 'win32', 'branch': 'mozilla-central', 'date': '2013-09-30', 'is_stub_installer': True},
     '2013-09-30-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer-stub.exe',
     'firefox/nightly/2013/09/2013-09-30-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer-stub.exe'),
    # Old file name format
    ({'platform': 'win64', 'branch': 'mozilla-central', 'date': '2013-09-30'},
     '2013-09-30-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64-x86_64.installer.exe',
     'firefox/nightly/2013/09/2013-09-30-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64-x86_64.installer.exe'),
    # New stub format
    ({'platform': 'win32', 'branch': 'mozilla-central', 'is_stub_installer': True},
     '2013-10-01-03-02-04-mozilla-central-Firefox Installer.en-US.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/Firefox Installer.en-US.exe'),
    ({'platform': 'win32', 'branch': 'mozilla-aurora'},
     '2013-10-01-03-02-04-mozilla-aurora-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-aurora/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win32', 'branch': 'ux'},
     '2013-10-01-03-02-04-ux-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-ux/firefox-27.0a1.en-US.win32.installer.exe')
]

thunderbird_tests = [
    ({'application': 'thunderbird', 'platform': 'linux', 'branch': 'comm-central'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'branch': 'comm-central'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'branch': 'comm-central'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.mac.dmg',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.mac.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win64', 'branch': 'comm-central'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win64-x86_64.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win64-x86_64.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'branch': 'comm-central', 'extension': 'txt'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.txt',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.txt'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central', 'locale': 'it'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.it.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.it.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central', 'locale': 'sv-SE'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.sv-SE.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.sv-SE.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central', 'build_id': '20130710110153'},
     '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central', 'date': '2013-07-10'},
     '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central',
      'date': '2013-07-10', 'build_number': 1},
     '2013-07-10-10-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/07/2013-07-10-10-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-aurora'},
     '2013-10-01-03-02-04-comm-aurora-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-aurora/thunderbird-27.0a1.en-US.win32.installer.exe'),
]

fennec_tests = [
    ({'application': 'fennec', 'platform': 'android-api-9', 'branch': 'mozilla-central'},
     '2016-02-01-03-02-41-mozilla-central-fennec-47.0a1.multi.android-arm.apk',
     'mobile/nightly/2016/02/2016-02-01-03-02-41-mozilla-central-android-api-9/fennec-47.0a1.multi.android-arm.apk'),
    ({'application': 'fennec', 'platform': 'android-api-11', 'branch': 'mozilla-central'},
     '2015-06-11-03-02-08-mozilla-central-fennec-41.0a1.multi.android-arm.apk',
     'mobile/nightly/2015/06/2015-06-11-03-02-08-mozilla-central-android-api-11/fennec-41.0a1.multi.android-arm.apk'),
    ({'application': 'fennec', 'platform': 'android-api-15', 'branch': 'mozilla-central'},
     '2016-02-01-03-02-41-mozilla-central-fennec-47.0a1.multi.android-arm.apk',
     'mobile/nightly/2016/02/2016-02-01-03-02-41-mozilla-central-android-api-15/fennec-47.0a1.multi.android-arm.apk'),
    ({'application': 'fennec', 'platform': 'android-x86', 'branch': 'mozilla-central'},
     '2016-02-01-03-02-41-mozilla-central-fennec-47.0a1.multi.android-i386.apk',
     'mobile/nightly/2016/02/2016-02-01-03-02-41-mozilla-central-android-x86/fennec-47.0a1.multi.android-i386.apk'),
    ({'application': 'fennec', 'platform': 'android-api-15', 'branch': 'mozilla-aurora'},
     '2016-02-02-00-40-08-mozilla-aurora-fennec-46.0a2.multi.android-arm.apk',
     'mobile/nightly/2016/02/2016-02-02-00-40-08-mozilla-aurora-android-api-15/fennec-46.0a2.multi.android-arm.apk'),
]


@pytest.mark.parametrize("args,filename,url", firefox_tests + thunderbird_tests + fennec_tests)
def test_scraper(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for DailyScraper"""

    scraper = DailyScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_target = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_target

    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
