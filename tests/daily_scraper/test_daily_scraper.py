#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
from urllib.parse import unquote

from mozdownload import DailyScraper
from mozdownload.utils import urljoin

firefox_tests = [
    ({'platform': 'win32'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win64'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64.installer.exe'),
    ({'platform': 'linux'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.tar.bz2',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'platform': 'linux64'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-x86_64.tar.bz2',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'platform': 'linux-arm64'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-aarch64.tar.bz2',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-aarch64.tar.bz2'),
    ({'platform': 'mac'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.mac.dmg',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.mac.dmg'),
    ({'platform': 'win32', 'branch': 'mozilla-central'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'linux', 'extension': 'txt'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.linux-i686.txt',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central/firefox-27.0a1.en-US.linux-i686.txt'),
    ({'platform': 'win32', 'locale': 'it'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.it.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.it.win32.installer.exe'),
    ({'platform': 'win32', 'locale': 'sv-SE'},
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.sv-SE.win32.installer.exe',
     'firefox/nightly/2013/10/2013-10-01-03-02-04-mozilla-central-l10n/firefox-27.0a1.sv-SE.win32.installer.exe'),
    ({'platform': 'win32', 'build_id': '20130706031213'},
     '2013-07-06-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/07/2013-07-06-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win32', 'date': '2013-07-02'},
     '2013-07-02-04-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/07/2013-07-02-04-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win32', 'date': '2013-07-02', 'build_number': 1},
     '2013-07-02-03-12-13-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
     'firefox/nightly/2013/07/2013-07-02-03-12-13-mozilla-central/firefox-27.0a1.en-US.win32.installer.exe'),
    # Old stub format
    ({'platform': 'win32', 'date': '2013-09-30', 'is_stub_installer': True},
     '2013-09-30-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer-stub.exe',
     'firefox/nightly/2013/09/2013-09-30-03-02-04-mozilla-central/firefox-27.0a1.en-US.win32.installer-stub.exe'),
    # Old file name format
    ({'platform': 'win64', 'date': '2013-09-30'},
     '2013-09-30-03-02-04-mozilla-central-firefox-27.0a1.en-US.win64-x86_64.installer.exe',
     'firefox/nightly/2013/09/2013-09-30-03-02-04-mozilla-central/firefox-27.0a1.en-US.win64-x86_64.installer.exe'),
    # New stub format
    ({'platform': 'win32', 'is_stub_installer': True},
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
    ({'application': 'thunderbird', 'platform': 'linux'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.mac.dmg',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.mac.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win64'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.win64-x86_64.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.win64-x86_64.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'branch': 'comm-central'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux', 'extension': 'txt'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.en-US.linux-i686.txt',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central/thunderbird-27.0a1.en-US.linux-i686.txt'),
    ({'application': 'thunderbird', 'platform': 'win32', 'locale': 'it'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.it.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.it.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'locale': 'sv-SE'},
     '2013-10-01-03-02-04-comm-central-thunderbird-27.0a1.sv-SE.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-central-l10n/thunderbird-27.0a1.sv-SE.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'build_id': '20130710110153'},
     '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'date': '2013-07-10'},
     '2013-07-10-11-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/07/2013-07-10-11-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'date': '2013-07-10', 'build_number': 1},
     '2013-07-10-10-01-53-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/07/2013-07-10-10-01-53-comm-central/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-aurora'},
     '2013-10-01-03-02-04-comm-aurora-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/nightly/2013/10/2013-10-01-03-02-04-comm-aurora/thunderbird-27.0a1.en-US.win32.installer.exe'),
]

fenix_tests = [
    ({'application': 'fenix', 'platform': 'android-arm64-v8a', 'date': '2022-11-14'},
     '2022-11-14-17-01-36-fenix-108.0b1.multi.android-arm64-v8a.apk',
     'fenix/nightly/2022/11/2022-11-14-17-01-36-fenix-108.0b1-android-arm64-v8a/fenix-108.0b1.multi.android-arm64-v8a.apk'),
    ({'application': 'fenix', 'platform': 'android-x86', 'date': '2022-11-14'},
     '2022-11-14-17-01-36-fenix-108.0b1.multi.android-x86.apk',
     'fenix/nightly/2022/11/2022-11-14-17-01-36-fenix-108.0b1-android-x86/fenix-108.0b1.multi.android-x86.apk'),
    ({'application': 'fenix', 'platform': 'android-armeabi-v7a', 'date': '2022-11-14'},
     '2022-11-14-17-01-36-fenix-108.0b1.multi.android-armeabi-v7a.apk',
     'fenix/nightly/2022/11/2022-11-14-17-01-36-fenix-108.0b1-android-armeabi-v7a/fenix-108.0b1.multi.android-armeabi-v7a.apk'),
    ({'application': 'fenix', 'platform': 'android-x86_64', 'date': '2022-11-14'},
     '2022-11-14-17-01-36-fenix-108.0b1.multi.android-x86_64.apk',
     'fenix/nightly/2022/11/2022-11-14-17-01-36-fenix-108.0b1-android-x86_64/fenix-108.0b1.multi.android-x86_64.apk'),
    ({'application': 'fenix', 'platform': 'android-arm64-v8a', 'date': '2022-11-14', 'locale': 'de'},
     '2022-11-14-17-01-36-fenix-108.0b1.multi.android-arm64-v8a.apk',
     'fenix/nightly/2022/11/2022-11-14-17-01-36-fenix-108.0b1-android-arm64-v8a/fenix-108.0b1.multi.android-arm64-v8a.apk'),
]

@pytest.mark.parametrize("args,filename,url", firefox_tests + thunderbird_tests + fenix_tests)
def test_scraper(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for DailyScraper"""

    scraper = DailyScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_target = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_target

    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
