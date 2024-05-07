#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
from urllib.parse import unquote

from mozdownload import ReleaseScraper
from mozdownload.utils import urljoin


@pytest.mark.parametrize("args,filename,url", [
    ({'application': 'fenix', 'platform': 'android-arm64-v8a', 'version': '120.1.0'},
     'fenix-120.1.0.multi.android-arm64-v8a.apk',
     'fenix/releases/120.1.0/android/fenix-120.1.0-android-arm64-v8a/fenix-120.1.0.multi.android-arm64-v8a.apk'),
    ({'application': 'fenix', 'platform': 'android-armeabi-v7a', 'version': '120.1.0'},
     'fenix-120.1.0.multi.android-armeabi-v7a.apk',
     'fenix/releases/120.1.0/android/fenix-120.1.0-android-armeabi-v7a/fenix-120.1.0.multi.android-armeabi-v7a.apk'),
    ({'application': 'fenix', 'platform': 'android-x86', 'version': '120.1.0'},
     'fenix-120.1.0.multi.android-x86.apk',
     'fenix/releases/120.1.0/android/fenix-120.1.0-android-x86/fenix-120.1.0.multi.android-x86.apk'),
    ({'application': 'fenix', 'platform': 'android-x86_64', 'version': '120.1.0'},
     'fenix-120.1.0.multi.android-x86_64.apk',
     'fenix/releases/120.1.0/android/fenix-120.1.0-android-x86_64/fenix-120.1.0.multi.android-x86_64.apk'),
    ({'application': 'fenix', 'platform': 'android-arm64-v8a', 'version': '120.1.0', 'locale': 'de'},
     'fenix-120.1.0.multi.android-arm64-v8a.apk',
     'fenix/releases/120.1.0/android/fenix-120.1.0-android-arm64-v8a/fenix-120.1.0.multi.android-arm64-v8a.apk'),
    ({'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1.en-US.win32.exe',
     'firefox/releases/23.0.1/win32/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1.en-US.win32.exe',
     'firefox/releases/23.0.1/win32/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': '23.0.1'},
     'firefox-23.0.1.en-US.win64.exe',
     'firefox/releases/23.0.1/win64/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'linux', 'version': '23.0.1'},
     'firefox-23.0.1.en-US.linux.tar.bz2',
     'firefox/releases/23.0.1/linux-i686/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': '23.0.1'},
     'firefox-23.0.1.en-US.linux64.tar.bz2',
     'firefox/releases/23.0.1/linux-x86_64/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': '23.0.1'},
     'firefox-23.0.1.en-US.mac.dmg',
     'firefox/releases/23.0.1/mac/en-US/Firefox 23.0.1.dmg'),
    ({'application': 'firefox', 'locale': 'de', 'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1.de.win32.exe',
     'firefox/releases/23.0.1/win32/de/Firefox Setup 23.0.1.exe'),
    # stub-installer (old format)
    ({'application': 'firefox', 'platform': 'win32', 'is_stub_installer': True, 'version': '21.0'},
     'firefox-21.0.en-US.win32-stub.exe',
     'firefox/releases/21.0/win32/en-US/Firefox Setup Stub 21.0.exe'),
    # stub-installer (new format)
    ({'application': 'firefox', 'platform': 'win32', 'is_stub_installer': True, 'version': '23.0.1'},
     'firefox-23.0.1.en-US.win32-stub.exe',
     'firefox/releases/23.0.1/win32/en-US/Firefox Installer.exe'),
    # stub-installer (new format)
    ({'application': 'firefox', 'platform': 'win64', 'is_stub_installer': True, 'version': '23.0.1'},
     'firefox-23.0.1.en-US.win64-stub.exe',
     'firefox/releases/23.0.1/win64/en-US/Firefox Installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '17.0'},
     'thunderbird-17.0.en-US.win32.exe',
     'thunderbird/releases/17.0/win32/en-US/Thunderbird Setup 17.0.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': '17.0'},
     'thunderbird-17.0.en-US.linux.tar.bz2',
     'thunderbird/releases/17.0/linux-i686/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': '17.0'},
     'thunderbird-17.0.en-US.linux64.tar.bz2',
     'thunderbird/releases/17.0/linux-x86_64/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': '17.0'},
     'thunderbird-17.0.en-US.mac.dmg',
     'thunderbird/releases/17.0/mac/en-US/Thunderbird 17.0.dmg'),
    ({'application': 'thunderbird', 'locale': 'de', 'platform': 'win32', 'version': '17.0'},
     'thunderbird-17.0.de.win32.exe',
     'thunderbird/releases/17.0/win32/de/Thunderbird Setup 17.0.exe'),
])
def test_release_scraper(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for ReleaseScraper"""

    scraper = ReleaseScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
