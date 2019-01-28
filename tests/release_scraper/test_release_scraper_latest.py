#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import urllib

import pytest

from mozdownload import ReleaseScraper
from mozdownload.utils import urljoin


@pytest.mark.parametrize("args,filename,url", [
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest'},
     'firefox-23.0.1.en-US.linux.tar.bz2',
     'firefox/releases/23.0.1/linux-i686/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': 'latest'},
     'firefox-23.0.1.en-US.linux64.tar.bz2',
     'firefox/releases/23.0.1/linux-x86_64/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': 'latest'},
     'firefox-23.0.1.en-US.mac.dmg',
     'firefox/releases/23.0.1/mac/en-US/Firefox 23.0.1.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': 'latest'},
     'firefox-23.0.1.en-US.win32.exe',
     'firefox/releases/23.0.1/win32/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': 'latest'},
     'firefox-23.0.1.en-US.win64.exe',
     'firefox/releases/23.0.1/win64/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest-beta'},
     'firefox-24.0b1.en-US.linux.tar.bz2',
     'firefox/releases/24.0b1/linux-i686/en-US/firefox-24.0b1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': 'latest-beta'},
     'firefox-24.0b1.en-US.linux64.tar.bz2',
     'firefox/releases/24.0b1/linux-x86_64/en-US/firefox-24.0b1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': 'latest-beta'},
     'firefox-24.0b1.en-US.mac.dmg',
     'firefox/releases/24.0b1/mac/en-US/Firefox 24.0b1.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': 'latest-beta'},
     'firefox-24.0b1.en-US.win32.exe',
     'firefox/releases/24.0b1/win32/en-US/Firefox Setup 24.0b1.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': 'latest-beta'},
     'firefox-24.0b1.en-US.win64.exe',
     'firefox/releases/24.0b1/win64/en-US/Firefox Setup 24.0b1.exe'),
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest-esr'},
     'firefox-24.0esr.en-US.linux.tar.bz2',
     'firefox/releases/24.0esr/linux-i686/en-US/firefox-24.0esr.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': 'latest-esr'},
     'firefox-24.0esr.en-US.linux64.tar.bz2',
     'firefox/releases/24.0esr/linux-x86_64/en-US/firefox-24.0esr.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': 'latest-esr'},
     'firefox-24.0esr.en-US.mac.dmg',
     'firefox/releases/24.0esr/mac/en-US/Firefox 24.0esr.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': 'latest-esr'},
     'firefox-24.0esr.en-US.win32.exe',
     'firefox/releases/24.0esr/win32/en-US/Firefox Setup 24.0esr.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': 'latest-esr'},
     'firefox-24.0esr.en-US.win64.exe',
     'firefox/releases/24.0esr/win64/en-US/Firefox Setup 24.0esr.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': 'latest'},
     'thunderbird-17.0.en-US.linux.tar.bz2',
     'thunderbird/releases/17.0/linux-i686/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': 'latest'},
     'thunderbird-17.0.en-US.linux64.tar.bz2',
     'thunderbird/releases/17.0/linux-x86_64/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': 'latest'},
     'thunderbird-17.0.en-US.mac.dmg',
     'thunderbird/releases/17.0/mac/en-US/Thunderbird 17.0.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest'},
     'thunderbird-17.0.en-US.win32.exe',
     'thunderbird/releases/17.0/win32/en-US/Thunderbird Setup 17.0.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': 'latest-beta'},
     'thunderbird-20.0b1.en-US.linux.tar.bz2',
     'thunderbird/releases/20.0b1/linux-i686/en-US/thunderbird-20.0b1.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': 'latest-beta'},
     'thunderbird-20.0b1.en-US.linux64.tar.bz2',
     'thunderbird/releases/20.0b1/linux-x86_64/en-US/thunderbird-20.0b1.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': 'latest-beta'},
     'thunderbird-20.0b1.en-US.mac.dmg',
     'thunderbird/releases/20.0b1/mac/en-US/Thunderbird 20.0b1.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest-beta'},
     'thunderbird-20.0b1.en-US.win32.exe',
     'thunderbird/releases/20.0b1/win32/en-US/Thunderbird Setup 20.0b1.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr.en-US.linux.tar.bz2',
     'thunderbird/releases/17.0.1esr/linux-i686/en-US/thunderbird-17.0.1esr.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr.en-US.linux64.tar.bz2',
     'thunderbird/releases/17.0.1esr/linux-x86_64/en-US/thunderbird-17.0.1esr.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr.en-US.mac.dmg',
     'thunderbird/releases/17.0.1esr/mac/en-US/Thunderbird 17.0.1esr.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr.en-US.win32.exe',
     'thunderbird/releases/17.0.1esr/win32/en-US/Thunderbird Setup 17.0.1esr.exe'),
])

def test_latest_build(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for latest release builds"""

    scraper = ReleaseScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert urllib.unquote(scraper.url) == urljoin(httpd.get_url(), url)
