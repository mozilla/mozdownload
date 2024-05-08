#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
from urllib.parse import unquote

from mozdownload import TinderboxScraper
from mozdownload.utils import urljoin


@pytest.mark.parametrize("args,filename,url", [
    ({'platform': 'win32'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'branch': 'mozilla-central', 'platform': 'win32'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'platform': 'win32'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    # -a firefox -p win32 --date 1374573725 --stub (old format)
    ({'application': 'firefox', 'date': '1374573725', 'is_stub_installer': True, 'platform': 'win32'},
     '1374573725-mozilla-central-firefox-25.0a1.en-US.win32.installer-stub.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374573725/firefox-25.0a1.en-US.win32.installer-stub.exe'),
    # -a firefox -p win32 --stub (new format)
    ({'application': 'firefox', 'platform': 'win32', 'date': '1374583608', 'is_stub_installer': True},
     '1374583608-mozilla-central-setup.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374583608/setup.exe'),
    ({'platform': 'linux'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.linux-i686.tar.bz2',
     'firefox/tinderbox-builds/mozilla-central-linux/'
     '1374583608/firefox-25.0a1.en-US.linux-i686.tar.bz2'),
    ({'platform': 'linux64'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.linux-x86_64.tar.bz2',
     'firefox/tinderbox-builds/mozilla-central-linux64/'
     '1374583608/firefox-25.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'application': 'firefox', 'platform': 'win32'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'platform': 'win64'},
     '1423517445-mozilla-central-firefox-38.0a1.en-US.win64.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win64/'
     '1423517445/firefox-38.0a1.en-US.win64.installer.exe'),
    # -a firefox -p win64 --branch=mozilla-central --date=2013-07-23 (old filename format)
    ({'application': 'firefox', 'platform': 'win64', 'date': '2013-07-23'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.win64-x86_64.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win64/'
     '1374583608/firefox-25.0a1.en-US.win64-x86_64.installer.exe'),
    ({'application': 'firefox', 'platform': 'mac64'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.mac.dmg',
     'firefox/tinderbox-builds/mozilla-central-macosx64/'
     '1374583608/firefox-25.0a1.en-US.mac.dmg'),
    ({'application': 'firefox', 'debug_build': True, 'platform': 'win32'},
     '1374583608-mozilla-central-debug-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32-debug/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'locale': 'de', 'platform': 'win32'},
     'mozilla-central-firefox-25.0a1.de.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-l10n/'
     'firefox-25.0a1.de.win32.installer.exe'),
    ({'application': 'firefox', 'locale': 'pt-PT', 'platform': 'win32'},
     'mozilla-central-firefox-25.0a1.pt-PT.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-l10n/'
     'firefox-25.0a1.pt-PT.win32.installer.exe'),
    ({'application': 'firefox', 'date': '2013-07-23', 'platform': 'win32'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'build_number': '1', 'date': '2013-07-23',
      'platform': 'win32'},
     '1374568307-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374568307/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'date': '1374573725', 'platform': 'win32'},
     '1374573725-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374573725/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'branch': 'mozilla-inbound', 'platform': 'win32'},
     '1374583608-mozilla-inbound-firefox-25.0a1.en-US.win32.installer.exe',
     'firefox/tinderbox-builds/mozilla-inbound-win32/'
     '1374583608/firefox-25.0a1.en-US.win32.installer.exe'),
    ({'application': 'firefox', 'extension': 'txt', 'platform': 'linux'},
     '1374583608-mozilla-central-firefox-25.0a1.en-US.linux-i686.txt',
     'firefox/tinderbox-builds/mozilla-central-linux/'
     '1374583608/firefox-25.0a1.en-US.linux-i686.txt'),
    ({'application': 'firefox', 'extension': 'txt', 'platform': 'win32'},
     '1374568307-mozilla-central-firefox-25.0a1.en-US.win32.txt',
     'firefox/tinderbox-builds/mozilla-central-win32/'
     '1374568307/firefox-25.0a1.en-US.win32.txt'),
    ({'application': 'firefox', 'extension': 'txt', 'platform': 'mac'},
     '1374568307-mozilla-central-firefox-25.0a1.en-US.mac.txt',
     'firefox/tinderbox-builds/mozilla-central-macosx64/'
     '1374568307/firefox-25.0a1.en-US.mac.txt'),

    ({'application': 'thunderbird', 'platform': 'linux'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
     'thunderbird/tinderbox-builds/comm-central-linux/'
     '1380362686/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2',
     'thunderbird/tinderbox-builds/comm-central-linux64/'
     '1380362686/thunderbird-27.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac64'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.mac.dmg',
     'thunderbird/tinderbox-builds/comm-central-macosx64/'
     '1380362686/thunderbird-27.0a1.en-US.mac.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-win32/'
     '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'platform': 'win64'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.win64-x86_64.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-win64/'
     '1380362686/thunderbird-27.0a1.en-US.win64-x86_64.installer.exe'),
    ({'application': 'thunderbird', 'branch': 'comm-central', 'platform': 'linux'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.linux-i686.tar.bz2',
     'thunderbird/tinderbox-builds/comm-central-linux/'
     '1380362686/thunderbird-27.0a1.en-US.linux-i686.tar.bz2'),
    ({'application': 'thunderbird', 'debug_build': True, 'platform': 'win32'},
     '1380362686-comm-central-debug-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-win32-debug/'
     '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'locale': 'de', 'platform': 'win32'},
     'comm-central-thunderbird-27.0a1.de.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-l10n/'
     'thunderbird-27.0a1.de.win32.installer.exe'),
    ({'application': 'thunderbird', 'locale': 'pt-PT', 'platform': 'win32'},
     'comm-central-thunderbird-27.0a1.pt-PT.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-l10n/'
     'thunderbird-27.0a1.pt-PT.win32.installer.exe'),
    ({'application': 'thunderbird', 'date': '2013-09-28', 'platform': 'win32'},
     '1380362686-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-win32/'
     '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'build_number': '1', 'date': '2013-09-28',
      'platform': 'win32'},
     '1380362527-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-win32/'
     '1380362527/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'date': '1380362527', 'platform': 'win32'},
     '1380362527-comm-central-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-central-win32/'
     '1380362527/thunderbird-27.0a1.en-US.win32.installer.exe'),
    ({'application': 'thunderbird', 'branch': 'comm-aurora', 'platform': 'win32'},
     '1380362686-comm-aurora-thunderbird-27.0a1.en-US.win32.installer.exe',
     'thunderbird/tinderbox-builds/comm-aurora-win32/'
     '1380362686/thunderbird-27.0a1.en-US.win32.installer.exe'),
])
def test_scraper(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for TinderboxScraper"""

    scraper = TinderboxScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
