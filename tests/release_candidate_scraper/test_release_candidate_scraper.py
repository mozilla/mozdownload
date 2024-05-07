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
    ({'application': 'firefox', 'platform': 'linux', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.linux.tar.bz2',
     'firefox/candidates/23.0.1-candidates/build3/linux-i686/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.linux64.tar.bz2',
     'firefox/candidates/23.0.1-candidates/build3/linux-x86_64/en-US/firefox-23.0.1.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.mac.dmg',
     'firefox/candidates/23.0.1-candidates/build3/mac/en-US/Firefox 23.0.1.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.win32.exe',
     'firefox/candidates/23.0.1-candidates/build3/win32/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.win64.exe',
     'firefox/candidates/23.0.1-candidates/build3/win64/en-US/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'locale': 'de', 'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1-build3.de.win32.exe',
     'firefox/candidates/23.0.1-candidates/build3/win32/de/Firefox Setup 23.0.1.exe'),
    ({'application': 'firefox', 'build_number': '1', 'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1-build1.en-US.win32.exe',
     'firefox/candidates/23.0.1-candidates/build1/win32/en-US/Firefox Setup 23.0.1.exe'),
    # stub-installer (old format)
    ({'application': 'firefox', 'is_stub_installer': True, 'platform': 'win32', 'version': '21.0'},
     'firefox-21.0-build1.en-US.win32-stub.exe',
     'firefox/candidates/21.0-candidates/build1/win32/en-US/Firefox Setup Stub 21.0.exe'),
    # stub-installer (new format)
    ({'application': 'firefox', 'is_stub_installer': True, 'platform': 'win32', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.win32-stub.exe',
     'firefox/candidates/23.0.1-candidates/build3/win32/en-US/Firefox Installer.exe'),
    # stub-installer (new format)
    ({'application': 'firefox', 'is_stub_installer': True, 'platform': 'win64', 'version': '23.0.1'},
     'firefox-23.0.1-build3.en-US.win64-stub.exe',
     'firefox/candidates/23.0.1-candidates/build3/win64/en-US/Firefox Installer.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': '17.0'},
     'thunderbird-17.0-build3.en-US.linux.tar.bz2',
     'thunderbird/candidates/17.0-candidates/build3/linux-i686/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': '17.0'},
     'thunderbird-17.0-build3.en-US.linux64.tar.bz2',
     'thunderbird/candidates/17.0-candidates/build3/linux-x86_64/en-US/thunderbird-17.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': '17.0'},
     'thunderbird-17.0-build3.en-US.mac.dmg',
     'thunderbird/candidates/17.0-candidates/build3/mac/en-US/Thunderbird 17.0.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '17.0'},
     'thunderbird-17.0-build3.en-US.win32.exe',
     'thunderbird/candidates/17.0-candidates/build3/win32/en-US/Thunderbird Setup 17.0.exe'),
    ({'application': 'thunderbird', 'locale': 'de', 'platform': 'win32', 'version': '17.0'},
     'thunderbird-17.0-build3.de.win32.exe',
     'thunderbird/candidates/17.0-candidates/build3/win32/de/Thunderbird Setup 17.0.exe'),
])
def test_scraper(httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for ReleaseCandidateScraper"""

    scraper = ReleaseCandidateScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
