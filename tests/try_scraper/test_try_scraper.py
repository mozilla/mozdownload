#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
from urllib.parse import unquote

from mozdownload import TryScraper
from mozdownload.utils import urljoin


@pytest.mark.parametrize("args,filename,url", [
    ({'platform': 'mac64', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-macosx64/firefox-38.0a1.en-US.mac.dmg'),
    ({'platform': 'mac', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-macosx64/firefox-38.0a1.en-US.mac.dmg'),
    ({'platform': 'linux64', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.linux-x86_64.tar.bz2',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-linux64/firefox-38.0a1.en-US.linux-x86_64.tar.bz2'),
    ({'platform': 'linux', 'revision': '8fcac92cfcad', 'debug_build': True},
     '8fcac92cfcad-debug-firefox-38.0a1.en-US.linux-i686.tar.bz2',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-linux-debug/firefox-38.0a1.en-US.linux-i686.tar.bz2'),
    ({'platform': 'win32', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.win32.installer.exe',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-win32/firefox-38.0a1.en-US.win32.installer.exe'),
    ({'platform': 'win64', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.win64.installer.exe',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-win64/firefox-38.0a1.en-US.win64.installer.exe')
])
def test_scraper(httpd, tmpdir, args, filename, url, mocker):
    """Testing various download scenarios for TryScraper"""
    query_builds_by_revision = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    query_builds_by_revision.return_value = [
        '/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-foobar/'
    ]
    scraper = TryScraper(destination=str(tmpdir),
                         base_url=httpd.get_url(),
                         **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert unquote(scraper.url) == urljoin(httpd.get_url(), url)
