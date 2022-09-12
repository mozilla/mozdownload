#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
from urllib.parse import unquote

from mozdownload import ReleaseCandidateScraper
from mozdownload.utils import urljoin


@pytest.mark.parametrize("args,filename,url", [
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest'},
     'firefox-23.0.1-build3.en-US.linux.tar.bz2',
     'firefox/candidates/23.0.1-candidates/build3/linux-i686/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': 'latest'},
     'firefox-23.0.1-build3.en-US.linux64.tar.bz2',
     'firefox/candidates/23.0.1-candidates/build3/linux-x86_64/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': 'latest'},
     'firefox-23.0.1-build3.en-US.mac.dmg',
     'firefox/candidates/23.0.1-candidates/build3/mac/en-US/Firefox 23.0.1.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': 'latest'},
     'firefox-23.0.1-build3.en-US.win32.exe',
     'firefox/candidates/23.0.1-candidates/build3/win32/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': 'latest'},
     'firefox-23.0.1-build3.en-US.win64.exe',
     'firefox/candidates/23.0.1-candidates/build3/win64/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest-beta'},
     'firefox-24.0b1-build1.en-US.linux.tar.bz2',
     'firefox/candidates/24.0b1-candidates/build1/linux-i686/en-US/firefox-24.0b1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': 'latest-beta'},
     'firefox-24.0b1-build1.en-US.linux64.tar.bz2',
     'firefox/candidates/24.0b1-candidates/build1/linux-x86_64/en-US/firefox-24.0b1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': 'latest-beta'},
     'firefox-24.0b1-build1.en-US.mac.dmg',
     'firefox/candidates/24.0b1-candidates/build1/mac/en-US/Firefox 24.0b1.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': 'latest-beta'},
     'firefox-24.0b1-build1.en-US.win32.exe',
     'firefox/candidates/24.0b1-candidates/build1/win32/en-US/Firefox Setup 24.0b1.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': 'latest-beta'},
     'firefox-24.0b1-build1.en-US.win64.exe',
     'firefox/candidates/24.0b1-candidates/build1/win64/en-US/Firefox Setup 24.0b1.exe'),
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest-esr'},
     'firefox-24.0esr-build1.en-US.linux.tar.bz2',
     'firefox/candidates/24.0esr-candidates/build1/linux-i686/en-US/firefox-24.0esr.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': 'latest-esr'},
     'firefox-24.0esr-build1.en-US.linux64.tar.bz2',
     'firefox/candidates/24.0esr-candidates/build1/linux-x86_64/en-US/firefox-24.0esr.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': 'latest-esr'},
     'firefox-24.0esr-build1.en-US.mac.dmg',
     'firefox/candidates/24.0esr-candidates/build1/mac/en-US/Firefox 24.0esr.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': 'latest-esr'},
     'firefox-24.0esr-build1.en-US.win32.exe',
     'firefox/candidates/24.0esr-candidates/build1/win32/en-US/Firefox Setup 24.0esr.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': 'latest-esr'},
     'firefox-24.0esr-build1.en-US.win64.exe',
     'firefox/candidates/24.0esr-candidates/build1/win64/en-US/Firefox Setup 24.0esr.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': 'latest'},
     'thunderbird-17.0-build3.en-US.linux.tar.bz2',
     'thunderbird/candidates/17.0-candidates/build3/linux-i686/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': 'latest'},
     'thunderbird-17.0-build3.en-US.linux64.tar.bz2',
     'thunderbird/candidates/17.0-candidates/build3/linux-x86_64/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': 'latest'},
     'thunderbird-17.0-build3.en-US.mac.dmg',
     'thunderbird/candidates/17.0-candidates/build3/mac/en-US/Thunderbird 17.0.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest'},
     'thunderbird-17.0-build3.en-US.win32.exe',
     'thunderbird/candidates/17.0-candidates/build3/win32/en-US/Thunderbird Setup 17.0.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': 'latest-beta'},
     'thunderbird-20.0b1-build1.en-US.linux.tar.bz2',
     'thunderbird/candidates/20.0b1-candidates/build1/linux-i686/en-US/thunderbird-20.0b1.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': 'latest-beta'},
     'thunderbird-20.0b1-build1.en-US.linux64.tar.bz2',
     'thunderbird/candidates/20.0b1-candidates/build1/linux-x86_64/en-US/thunderbird-20.0b1.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': 'latest-beta'},
     'thunderbird-20.0b1-build1.en-US.mac.dmg',
     'thunderbird/candidates/20.0b1-candidates/build1/mac/en-US/Thunderbird 20.0b1.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest-beta'},
     'thunderbird-20.0b1-build1.en-US.win32.exe',
     'thunderbird/candidates/20.0b1-candidates/build1/win32/en-US/Thunderbird Setup 20.0b1.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr-build1.en-US.linux.tar.bz2',
     'thunderbird/candidates/17.0.1esr-candidates/build1/linux-i686/en-US/thunderbird-17.0.1esr.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr-build1.en-US.linux64.tar.bz2',
     'thunderbird/candidates/17.0.1esr-candidates/build1/linux-x86_64/en-US/thunderbird-17.0.1esr.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr-build1.en-US.mac.dmg',
     'thunderbird/candidates/17.0.1esr-candidates/build1/mac/en-US/Thunderbird 17.0.1esr.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest-esr'},
     'thunderbird-17.0.1esr-build1.en-US.win32.exe',
     'thunderbird/candidates/17.0.1esr-candidates/build1/win32/en-US/Thunderbird Setup 17.0.1esr.exe'),
])
def test_latest_build(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for latest release candidate builds"""

    scraper = ReleaseCandidateScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
